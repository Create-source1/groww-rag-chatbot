"""Prompt construction for LLM generation."""
from app.models.schemas import RetrievedChunk, Message
from app.config import settings


class PromptBuilder:
    """Builds prompts from retrieved chunks and conversation history."""

    SYSTEM_PROMPT = (
        "You are a helpful assistant for the Groww investment platform. "
        "Answer the user's question based on the provided context. "
        "If the context does not contain enough information, say "
        "\"I don't have enough information to answer that question.\""
    )

    def build_messages(self, query: str, chunks: list[RetrievedChunk],
                       history: list[Message] = None) -> list[dict]:
        """Build a list of chat messages for the LLM."""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add conversation history (limited)
        if history:
            for msg in history[-settings.max_history:]:
                messages.append({"role": msg.role, "content": msg.content})

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                "--- Context {} ---\n{}\n(Source: {})".format(
                    i, chunk.text, chunk.document_title
                )
            )

        context_str = "\n\n".join(context_parts) if context_parts else "No relevant context found."

        # Build user message with context
        user_message = (
            "CONTEXT:\n{}\n\n"
            "USER QUESTION: {}\n\n"
            "ANSWER:"
        ).format(context_str, query)
        messages.append({"role": "user", "content": user_message})

        return messages
