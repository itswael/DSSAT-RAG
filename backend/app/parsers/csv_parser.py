"""CSV parser for DSSAT summary files."""
import csv
from typing import List, Dict, Any, Optional


class CSVParser:
    """Parser for DSSAT summary CSV files."""

    @staticmethod
    def parse_summary_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a DSSAT summary CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of dictionaries containing row data
        """
        rows = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows

    @staticmethod
    def parse_summary_csv_with_metadata(
        file_path: str,
    ) -> Dict[str, Any]:
        """
        Parse a DSSAT summary CSV file with metadata.

        Args:
            file_path: Path to the CSV file

        Returns:
            Dictionary containing metadata and data
        """
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find where header starts (first line starting with "EXP")
        header_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("EXP"):
                header_idx = i
                break

        metadata = {
            "file_path": file_path,
            "total_rows": len(lines) - header_idx - 1,
            "header_line": header_idx,
        }

        # Parse data rows
        data = []
        reader = csv.DictReader(lines[header_idx:])
        for row in reader:
            data.append(row)

        return {"metadata": metadata, "data": data}

    @staticmethod
    def clean_value(value: str) -> Any:
        """
        Clean a CSV value.

        Args:
            value: Raw string value

        Returns:
            Cleaned value (converted to appropriate type)
        """
        if not value or value.strip() == "" or value.strip() == ".":
            return None

        value = value.strip()

        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            pass

        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value


def parse_summary_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a DSSAT summary CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        List of dictionaries containing row data
    """
    return CSVParser.parse_summary_csv(file_path)
