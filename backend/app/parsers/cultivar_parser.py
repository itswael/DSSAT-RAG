"""Parser for DSSAT cultivar (.CUL) files."""
import re
from typing import List, Dict, Any, Optional

from app.models.canonical import CanonicalSimulation


class CultivarParser:
    """Parser for DSSAT cultivar files."""

    @staticmethod
    def parse_cul_file(file_path: str) -> List[CanonicalSimulation]:
        """
        Parse a .CUL file.

        Args:
            file_path: Path to the CUL file

        Returns:
            List of CanonicalSimulation instances
        """
        simulations = []

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse cultivar entries (simplified parsing)
        # CUL files contain cultivar definitions with parameters
        lines = content.split("\n")

        current_cultivar: Dict[str, Any] = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"):
                continue

            # Parse key-value pairs
            if "=" in line:
                key, value = line.split("=", 1)
                current_cultivar[key.strip()] = value.strip()

            # New cultivar entry starts with a name
            elif re.match(r"^[A-Z0-9_]+", line):
                if current_cultivar:
                    sim = CultivarParser._create_simulation_from_cul(current_cultivar)
                    simulations.append(sim)
                current_cultivar = {"name": line.strip()}

        # Don't forget the last cultivar
        if current_cultivar:
            sim = CultivarParser._create_simulation_from_cul(current_cultivar)
            simulations.append(sim)

        return simulations

    @staticmethod
    def _create_simulation_from_cul(
        cul_data: Dict[str, Any],
    ) -> CanonicalSimulation:
        """
        Create a simulation from CUL data.

        Args:
            cul_data: Cultivar data dictionary

        Returns:
            CanonicalSimulation instance
        """
        return CanonicalSimulation(
            simulation={
                "run_name": cul_data.get("name", ""),
                "experiment_name": cul_data.get("CR", ""),
                "crop": cul_data.get("CROP", ""),
                "cultivar": cul_data.get("NAME", ""),
                "irrigation": cul_data.get("IRRIG", ""),
                "nitrogen_level": cul_data.get("NITROGEN", ""),
                "planting_stage": cul_data.get("PLANTING", ""),
                "harvest_area": None,
                "year": 2024,
            },
            location={
                "latitude": None,
                "longitude": None,
                "country": None,
                "state": None,
                "district": None,
                "ecological_zone": cul_data.get("ECOZONE", ""),
            },
            outputs={},
        )


def parse_cul_file(file_path: str) -> List[CanonicalSimulation]:
    """
    Parse a .CUL file.

    Args:
        file_path: Path to the CUL file

    Returns:
        List of CanonicalSimulation instances
    """
    return CultivarParser.parse_cul_file(file_path)
