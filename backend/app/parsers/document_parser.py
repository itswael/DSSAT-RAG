"""Parser for document files (PDF, Markdown, TXT)."""
import os
from typing import List, Dict, Any

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

from app.models.canonical import CanonicalDocument


class DocumentParser:
    """Parser for document files."""

    @staticmethod
    def parse_pdf(file_path: str) -> List[CanonicalDocument]:
        """
        Parse a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of CanonicalDocument instances
        """
        if not PYPDF_AVAILABLE:
            return [
                CanonicalDocument(
                    title=os.path.basename(file_path),
                    text="PDF parsing requires pypdf library",
                    metadata={
                        "source_file": file_path,
                        "document_type": "pdf",
                    },
                )
            ]

        documents = []

        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""

                documents.append(
                    CanonicalDocument(
                        title=f"Page {page_num + 1}",
                        text=text,
                        metadata={
                            "source_file": file_path,
                            "page_number": page_num + 1,
                            "document_type": "pdf",
                        },
                    )
                )

        return documents

    @staticmethod
    def parse_markdown(file_path: str) -> List[CanonicalDocument]:
        """
        Parse a Markdown file.

        Args:
            file_path: Path to the Markdown file

        Returns:
            List of CanonicalDocument instances
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title from first heading
        title = os.path.basename(file_path)
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        return [
            CanonicalDocument(
                title=title,
                text=content,
                metadata={
                    "source_file": file_path,
                    "document_type": "markdown",
                },
            )
        ]

    @staticmethod
    def parse_txt(file_path: str) -> List[CanonicalDocument]:
        """
        Parse a TXT file.

        Args:
            file_path: Path to the TXT file

        Returns:
            List of CanonicalDocument instances
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return [
            CanonicalDocument(
                title=os.path.basename(file_path),
                text=content,
                metadata={
                    "source_file": file_path,
                    "document_type": "txt",
                },
            )
        ]

    @classmethod
    def parse_document(cls, file_path: str) -> List[CanonicalDocument]:
        """
        Parse a document file based on extension.

        Args:
            file_path: Path to the document file

        Returns:
            List of CanonicalDocument instances
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return cls.parse_pdf(file_path)
        elif ext in (".md", ".markdown"):
            return cls.parse_markdown(file_path)
        elif ext == ".txt":
            return cls.parse_txt(file_path)
        else:
            # Default to text parsing
            return cls.parse_txt(file_path)


def parse_document_file(file_path: str) -> List[CanonicalDocument]:
    """
    Parse a document file.

    Args:
        file_path: Path to the document file

    Returns:
        List of CanonicalDocument instances
    """
    return DocumentParser.parse_document(file_path)
