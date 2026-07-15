"""Parser for DSSAT species (.SPE) files."""
from typing import List, Dict, Any

from app.models.canonical import CanonicalSimulation


class SpeciesParser:
    """Parser for DSSAT species files."""

    @staticmethod
    def parse_spe_file(file_path: str) -> List[CanonicalSimulation]:
        """
        Parse a .SPE file.

        Args:
            file_path: Path to the SPE file

        Returns:
            List of CanonicalSimulation instances
        """
        simulations = []

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")

        current_species: Dict[str, Any] = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"):
                continue

            # Parse key-value pairs
            if "=" in line:
                key, value = line.split("=", 1)
                current_species[key.strip()] = value.strip()

            # New species entry starts with a name
            elif line and not line.startswith("="):
                if current_species:
                    sim = SpeciesParser._create_simulation_from_spe(current_species)
                    simulations.append(sim)
                current_species = {"name": line}

        # Don't forget the last species
        if current_species:
            sim = SpeciesParser._create_simulation_from_spe(current_species)
            simulations.append(sim)

        return simulations

    @staticmethod
    def _create_simulation_from_spe(
        spe_data: Dict[str, Any],
    ) -> CanonicalSimulation:
        """
        Create a simulation from SPE data.

        Args:
            spe_data: Species data dictionary

        Returns:
            CanonicalSimulation instance
        """
        return CanonicalSimulation(
            simulation={
                "run_name": spe_data.get("name", ""),
                "experiment_name": spe_data.get("SPECIES", ""),
                "crop": spe_data.get("CROP", ""),
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
                "country": None,
                "state": None,
                "district": None,
                "ecological_zone": spe_data.get("ECOZONE", ""),
            },
            outputs={},
        )


def parse_spe_file(file_path: str) -> List[CanonicalSimulation]:
    """
    Parse a .SPE file.

    Args:
        file_path: Path to the SPE file

    Returns:
        List of CanonicalSimulation instances
    """
    return SpeciesParser.parse_spe_file(file_path)
