"""Parser for DSSAT ecotype (.ECO) files."""
from typing import List, Dict, Any

from app.models.canonical import CanonicalSimulation


class EcotypeParser:
    """Parser for DSSAT ecotype files."""

    @staticmethod
    def parse_eco_file(file_path: str) -> List[CanonicalSimulation]:
        """
        Parse a .ECO file.

        Args:
            file_path: Path to the ECO file

        Returns:
            List of CanonicalSimulation instances
        """
        simulations = []

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")

        current_ecotype: Dict[str, Any] = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"):
                continue

            # Parse key-value pairs
            if "=" in line:
                key, value = line.split("=", 1)
                current_ecotype[key.strip()] = value.strip()

            # New ecotype entry starts with a name
            elif line and not line.startswith("="):
                if current_ecotype:
                    sim = EcotypeParser._create_simulation_from_eco(current_ecotype)
                    simulations.append(sim)
                current_ecotype = {"name": line}

        # Don't forget the last ecotype
        if current_ecotype:
            sim = EcotypeParser._create_simulation_from_eco(current_ecotype)
            simulations.append(sim)

        return simulations

    @staticmethod
    def _create_simulation_from_eco(
        eco_data: Dict[str, Any],
    ) -> CanonicalSimulation:
        """
        Create a simulation from ECO data.

        Args:
            eco_data: Ecotype data dictionary

        Returns:
            CanonicalSimulation instance
        """
        return CanonicalSimulation(
            simulation={
                "run_name": eco_data.get("name", ""),
                "experiment_name": eco_data.get("ECOZONE", ""),
                "crop": eco_data.get("CROP", ""),
                "cultivar": "",
                "irrigation": "",
                "nitrogen_level": "",
                "planting_stage": "",
                "harvest_area": None,
                "year": 2024,
            },
            location={
                "latitude": None,
                "longitude": None,
                "country": eco_data.get("COUNTRY", ""),
                "state": eco_data.get("STATE", ""),
                "district": eco_data.get("DISTRICT", ""),
                "ecological_zone": eco_data.get("ECOZONE", ""),
            },
            outputs={},
        )


def parse_eco_file(file_path: str) -> List[CanonicalSimulation]:
    """
    Parse a .ECO file.

    Args:
        file_path: Path to the ECO file

    Returns:
        List of CanonicalSimulation instances
    """
    return EcotypeParser.parse_eco_file(file_path)
