"""Parser for DSSAT CDE files."""
import re
from typing import List, Dict, Any

from app.models.canonical import CanonicalCDE


class CDEParser:
    """Parser for DSSAT CDE (Crop Data Exchange) files."""

    @staticmethod
    def parse_cde_file(file_path: str) -> List[CanonicalCDE]:
        """
        Parse a .CDE file.

        Args:
            file_path: Path to the CDE file

        Returns:
            List of CanonicalCDE instances
        """
        entities = []

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")

        current_entity: Dict[str, Any] = {}
        entity_type = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"):
                continue

            # Detect entity type from section headers
            if line.startswith("[") and line.endswith("]"):
                if current_entity and entity_type:
                    cde = CDEParser._create_cde_from_data(current_entity, entity_type)
                    entities.append(cde)
                entity_type = line.strip("[]")
                current_entity = {}
                continue

            # Parse key-value pairs
            if "=" in line:
                key, value = line.split("=", 1)
                current_entity[key.strip()] = value.strip()

        # Don't forget the last entity
        if current_entity and entity_type:
            cde = CDEParser._create_cde_from_data(current_entity, entity_type)
            entities.append(cde)

        return entities

    @staticmethod
    def _create_cde_from_data(
        data: Dict[str, Any],
        entity_type: str,
    ) -> CanonicalCDE:
        """
        Create a CDE entity from data.

        Args:
            data: Entity data dictionary
            entity_type: Type of entity (variable, relationship, etc.)

        Returns:
            CanonicalCDE instance
        """
        return CanonicalCDE(
            entity_type=entity_type,
            code=data.get("CODE", ""),
            attributes={
                "name": data.get("NAME", ""),
                "description": data.get("DESCRIPTION", ""),
                "unit": data.get("UNIT", ""),
                "type": data.get("TYPE", ""),
                **data,
            },
        )


def parse_cde_file(file_path: str) -> List[CanonicalCDE]:
    """
    Parse a .CDE file.

    Args:
        file_path: Path to the CDE file

    Returns:
        List of CanonicalCDE instances
    """
    return CDEParser.parse_cde_file(file_path)
