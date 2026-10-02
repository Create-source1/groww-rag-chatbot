"""Query processing pipeline orchestrator."""
import re

from app.models.schemas import Message
from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder
from app.pipeline.components.retriever import Retriever
from app.pipeline.components.prompt_builder import PromptBuilder
from app.pipeline.components.llm_client import LLMClient, create_llm_client
from app.config import settings

# Words that carry no topical meaning (including fund-name words, which the
# metadata filter already handles).
_CONCEPT_STOPWORDS = {
    "what", "is", "the", "of", "a", "an", "for", "in", "on", "how", "to",
    "do", "does", "i", "my", "me", "and", "or", "can", "tell", "give",
    "which", "when", "about", "with", "are", "it", "its", "this", "that",
    "hdfc", "large", "small", "cap", "balanced", "advantage", "elss",
    "tax", "saver", "equity", "flexi", "fund", "direct", "growth",
}

# Official page URL for each scheme document (used as the citation link).
SOURCE_URLS = {
    "hdfc_large_cap_fund": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "hdfc_equity_flexi_cap_fund": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "hdfc_elss_tax_saver_fund": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "hdfc_small_cap_fund": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "hdfc_balanced_advantage_fund": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
}


def _concept_keywords(query: str) -> list[str]:
    """Meaningful terms left after removing question/fund-name stopwords."""
    words = re.findall(r"[a-z0-9]+", query.lower())
    return [w for w in words if w not in _CONCEPT_STOPWORDS and len(w) > 2]


class QueryPipeline:
    """Orchestrates the full RAG query flow."""

    def __init__(self, vector_store: VectorStore, embedder: Embedder,
                 llm_client: LLMClient = None):
        self.retriever = Retriever(vector_store, embedder)
        self.prompt_builder = PromptBuilder()
        self.llm_client = llm_client or create_llm_client()

    def _detect_where(self, query: str) -> dict:
        """Build a metadata filter based on fund keywords in the query."""
        q = query.lower()
        title_keywords = [
            ("hdfc_large_cap_fund", ["large cap", "large-cap", "largecap"]),
            ("hdfc_small_cap_fund", ["small cap", "small-cap", "smallcap"]),
            ("hdfc_balanced_advantage_fund", ["balanced advantage", "balanced", "hybrid"]),
            ("hdfc_elss_tax_saver_fund", ["elss", "tax saver", "tax-saver"]),
            ("hdfc_equity_flexi_cap_fund", ["flexi cap", "flexi-cap", "flexicap", "equity fund", "multi cap"]),
        ]
        matched = [title for title, kws in title_keywords if any(k in q for k in kws)]
        if not matched:
            return None
        if len(matched) == 1:
            return {"document_title": matched[0]}
        return {"document_title": {"$in": matched}}

    def process(self, query: str, history: list[Message] = None) -> dict:
        """Process a user query and return response with sources."""
        # 0. Make the query self-contained for retrieval: only fall back to
        # the last user message when this query names no fund itself
        # (e.g. follow-ups like "Who is the other manager?").
        where = self._detect_where(query)
        search_text = query
        if where is None and history:
            last_user = next((m.content for m in reversed(history) if m.role == "user"), None)
            if last_user:
                search_text = f"{last_user}\n{query}"
                where = self._detect_where(search_text)

        pool_k = max(settings.top_k * 3, 30)
        query_embedding = self.retriever.embedder.encode_query(search_text)
        pool = self.retriever.vector_store.search(query_embedding, top_k=pool_k, where=where)

        if not pool:
            return {
                "response": (
                    "I'm sorry, I couldn't find relevant information "
                    "in my knowledge base. Could you rephrase your question?"
                ),
                "sources": []
            }

        # Step 1b: Re-rank by concept-keyword coverage, then similarity.
        # Vector search alone ranks fund-name/about chunks high even when
        # the actual fact chunk contains the exact answer terms.
        keywords = _concept_keywords(search_text)

        # 1c: Merge in literal-keyword matches so fact chunks that the
        # embedding model ranked too low are still considered. Also try the
        # first 5 letters of each keyword as a loose stem (manager/manages/management).
        literal_terms = []
        for kw in keywords[:3]:
            literal_terms.append(kw)
            if len(kw) > 5:
                literal_terms.append(kw[:5])
        for kw in literal_terms:
            for literal_chunk in self.retriever.retrieve_literal(kw, where=where):
                if literal_chunk.chunk_id not in {c.chunk_id for c in pool}:
                    pool.append(literal_chunk)

        if keywords:
            def coverage(chunk):
                text = chunk.text.lower()
                # match on loose stems so 'manager' also matches 'manages' etc.
                return sum(1 for k in keywords if k in text or (len(k) > 5 and k[:5] in text)) / len(keywords)
            pool = sorted(pool, key=lambda c: (coverage(c), c.similarity_score), reverse=True)

        # Single fund matched: include the whole document (it's small) so
        # details that don't rank well by embedding (like the second
        # fund-manager card) are still in the context for the LLM.
        if where and where.get("document_title") and "$in" not in str(where):
            full = self.retriever.vector_store.collection.get(
                where=where, include=["documents", "metadatas"]
            )
            chunks = []
            for _id, text, meta in zip(full["ids"], full["documents"], full["metadatas"]):
                from app.models.schemas import RetrievedChunk
                chunks.append(RetrievedChunk(
                    chunk_id=_id,
                    document_title=meta.get("document_title", "Unknown"),
                    source=meta.get("source", ""),
                    chunk_index=meta.get("chunk_index", 0),
                    text=text,
                    similarity_score=0.5,
                ))
            chunks.sort(key=lambda c: c.chunk_index)
        else:
            chunks = pool[:settings.top_k]

        # Step 2: Handle no results
        if not chunks:
            return {
                "response": (
                    "I'm sorry, I couldn't find relevant information "
                    "in my knowledge base. Could you rephrase your question?"
                ),
                "sources": []
            }

        # Step 3: Build prompt
        messages = self.prompt_builder.build_messages(query, chunks, history)

        # Step 4: Generate response
        try:
            response_text = self.llm_client.generate(messages)
        except Exception as e:
            response_text = (
                "I'm having trouble generating a response right now. "
                "Please try again in a moment."
            )

        # Step 5: Format sources
        sources = []
        seen_urls = set()
        for chunk in chunks:
            url = SOURCE_URLS.get(chunk.document_title, chunk.source)
            if url in seen_urls:
                continue
            seen_urls.add(url)
            sources.append({
                "document_title": chunk.document_title,
                "source": url,
                "chunk_index": chunk.chunk_index,
                "similarity_score": round(chunk.similarity_score, 4)
            })

        return {
            "response": response_text,
            "sources": sources
        }
