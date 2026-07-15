"""File type detector for DSSAT data files."""
import os
from typing import Optional, Dict, Any


class FileTypeDetector:
    """Detects file types based on extension and content."""

    # Supported file extensions
    SUMMARY_CSV = "summary.csv"
    CULTIVAR = ".CUL"
    ECOTYPE = ".ECO"
    SPECIES = ".SPE"
    CDE = ".CDE"
    PDF = ".pdf"
    MARKDOWN = ".md"
    TEXT = ".txt"

    # File type mappings
    FILE_TYPES = {
        "csv": "summary_csv",
        "cul": "cultivar",
        "eco": "ecotype",
        "spe": "species",
        "cde": "cde",
        "pdf": "document",
        "md": "document",
        "txt": "document",
    }

    @classmethod
    def detect_type(cls, file_path: str) -> Optional[str]:
        """
        Detect the type of a file based on extension.

        Args:
            file_path: Path to the file

        Returns:
            File type string or None if not supported
        """
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")

        return cls.FILE_TYPES.get(ext)

    @classmethod
    def detect_type_from_filename(cls, filename: str) -> Optional[str]:
        """
        Detect file type from filename.

        Args:
            filename: Filename to detect

        Returns:
            File type string or None if not supported
        """
        ext = os.path.splitext(filename)[1].lower().lstrip(".")

        return cls.FILE_TYPES.get(ext)

    @classmethod
    def get_supported_types(cls) -> Dict[str, str]:
        """
        Get mapping of extensions to file types.

        Returns:
            Dictionary mapping extensions to file types
        """
        return cls.FILE_TYPES.copy()

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        Check if a file type is supported.

        Args:
            file_path: Path to the file

        Returns:
            True if supported, False otherwise
        """
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")

        return ext in cls.FILE_TYPES


def detect_file_type(file_path: str) -> Optional[str]:
    """
    Detect file type from path.

    Args:
        file_path: Path to the file

    Returns:
        File type string or None
    """
    return FileTypeDetector.detect_type(file_path)


def is_supported_file(file_path: str) -> bool:
    """
    Check if file is supported.

    Args:
        file_path: Path to the file

    Returns:
        True if supported, False otherwise
    """
    return FileTypeDetector.is_supported(file_path)
