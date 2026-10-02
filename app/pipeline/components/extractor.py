"""Text extraction from various document formats."""
import os
from pathlib import Path


class DocumentParseException(Exception):
    """Raised when a document cannot be parsed."""
    pass


class TextExtractor:
    """Extracts raw text from PDF, TXT, MD, and DOCX files."""

    SUPPORTED_FORMATS = {".pdf", ".txt", ".md", ".docx"}

    def extract(self, file_path: str) -> str:
        """Extract text from a file based on its extension."""
        ext = Path(file_path).suffix.lower()

        if ext not in self.SUPPORTED_FORMATS:
            raise DocumentParseException(f"Unsupported file format: {ext}")

        if not os.path.exists(file_path):
            raise DocumentParseException(f"File not found: {file_path}")

        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext == ".docx":
            return self._extract_docx(file_path)
        else:
            return self._extract_text(file_path)

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n\n".join(text_parts)
        except Exception as e:
            raise DocumentParseException(f"Failed to parse PDF: {e}")

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            return "\n\n".join(text_parts)
        except Exception as e:
            raise DocumentParseException(f"Failed to parse DOCX: {e}")

    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text files (TXT, MD)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            raise DocumentParseException(f"Failed to read text file: {e}")
