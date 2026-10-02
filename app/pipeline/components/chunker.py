"""Text chunking for document segmentation."""
from app.models.schemas import Chunk
from app.config import settings


class Chunker:
    """Splits text into overlapping chunks using LangChain."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        from langchain_text_splitters import RecursiveCharacterTextSplitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_text(self, text: str, document_id: str,
                  document_title: str, source: str) -> list[Chunk]:
        """Split text into chunks and return Chunk objects."""
        raw_chunks = self.splitter.split_text(text)

        chunks = []
        for i, chunk_text in enumerate(raw_chunks):
            chunks.append(Chunk(
                document_id=document_id,
                document_title=document_title,
                source=source,
                chunk_index=i,
                text=chunk_text.strip(),
                token_count=len(chunk_text.split())
            ))

        return chunks
