"""CDE Service - Crop Data Exchange information and definitions."""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class CDEService:
    """Service for CDE (Crop Data Exchange) information."""
    
    # Predefined variable definitions
    VARIABLE_DEFINITIONS: Dict[str, Dict[str, str]] = {
        "HWAM": {
            "full_name": "Harvested Weight of Dry Matter",
            "description": "Total dry matter yield at harvest, including grain and biomass",
            "unit": "kg/ha",
            "category": "yield"
        },
        "YIELD": {
            "full_name": "Harvest Yield",
            "description": "Grain yield at harvest",
            "unit": "kg/ha",
            "category": "yield"
        },
        "LAI": {
            "full_name": "Leaf Area Index",
            "description": "Total leaf area per unit ground area",
            "unit": "m²/m²",
            "category": "growth"
        },
        "ET": {
            "full_name": "Evapotranspiration",
            "description": "Water loss from soil and plants to atmosphere",
            "unit": "mm",
            "category": "water"
        },
        "GDD": {
            "full_name": "Growing Degree Days",
            "description": "Accumulated heat units for crop development",
            "unit": "°C-days",
            "category": "development"
        },
        "NUP": {
            "full_name": "Nitrogen Uptake",
            "description": "Total nitrogen absorbed by the crop",
            "unit": "kg/ha",
            "category": "nutrient"
        },
        "AWAD": {
            "full_name": "Average Water Availability in Domain",
            "description": "Soil water content averaged over root zone",
            "unit": "mm",
            "category": "water"
        },
        "BIO": {
            "full_name": "Biomass",
            "description": "Total above-ground biomass",
            "unit": "kg/ha",
            "category": "biomass"
        },
        "RAD": {
            "full_name": "Radiation Interception",
            "description": "Solar radiation intercepted by crop canopy",
            "unit": "MJ/m²",
            "category": "energy"
        },
        "NRFL": {
            "full_name": "Nitrogen Reflection",
            "description": "Nitrogen reflected from crop canopy",
            "unit": "kg/ha",
            "category": "nutrient"
        }
    }
    
    # Variable relationships
    VARIABLE_RELATIONSHIPS: Dict[str, List[str]] = {
        "HWAM": ["LAI", "ET", "GDD", "NUP"],
        "YIELD": ["LAI", "ET", "AWAD", "RAD"],
        "BIO": ["RAD", "ET", "NUP"],
        "LAI": ["GDD", "NUP", "NRFL"]
    }
    
    # Common cultivars by crop
    CULTIVAR_INFO: Dict[str, List[Dict[str, str]]] = {
        "Maize": [
            {"name": "P3396", "maturity_group": "0.3", "yield_potential": "high"},
            {"name": "P34R05", "maturity_group": "0.4", "yield_potential": "high"},
            {"name": "P39G08", "maturity_group": "0.9", "yield_potential": "medium"}
        ],
        "Wheat": [
            {"name": "Sonalika", "maturity": "short", "disease_resistance": "good"},
            {"name": "HD2967", "maturity": "medium", "disease_resistance": "excellent"}
        ],
        "Rice": [
            {"name": "IR8", "maturity": "medium", "yield_potential": "high"},
            {"name": "IR36", "maturity": "short", "disease_resistance": "good"}
        ]
    }
    
    # Species information
    SPECIES_INFO: Dict[str, Dict[str, Any]] = {
        "Maize": {
            "scientific_name": "Zea mays",
            "growth_cycle_days": 90-120,
            "optimal_temperature": "20-30°C",
            "optimal_ph": "5.5-7.0"
        },
        "Wheat": {
            "scientific_name": "Triticum aestivum",
            "growth_cycle_days": 100-130,
            "optimal_temperature": "15-25°C",
            "optimal_ph": "6.0-7.5"
        },
        "Rice": {
            "scientific_name": "Oryza sativa",
            "growth_cycle_days": 90-150,
            "optimal_temperature": "20-35°C",
            "optimal_ph": "5.5-6.5"
        }
    }
    
    # Synonyms
    VARIABLE_SYNONYMS: Dict[str, List[str]] = {
        "HWAM": ["harvest_yield", "dry_matter", "total_yield"],
        "YIELD": ["grain_yield", "yield_grain"],
        "LAI": ["leaf_area_index"],
        "ET": ["evapotranspiration", "water_loss"],
        "GDD": ["growing_degree_days", "heat_units"]
    }
    
    async def get_variable_definition(self, variable_code: str) -> Optional[Dict[str, str]]:
        """
        Get definition for a variable code.
        
        Args:
            variable_code: Variable code (e.g., HWAM)
            
        Returns:
            Definition dictionary or None
        """
        return self.VARIABLE_DEFINITIONS.get(variable_code)
    
    async def get_variable_relationships(self, variable_code: str) -> List[str]:
        """
        Get related variables for a variable.
        
        Args:
            variable_code: Variable code
            
        Returns:
            List of related variable codes
        """
        return self.VARIABLE_RELATIONSHIPS.get(variable_code, [])
    
    async def get_cultivar_info(self, crop: str) -> List[Dict[str, Any]]:
        """
        Get cultivar information for a crop.
        
        Args:
            crop: Crop name
            
        Returns:
            List of cultivar information
        """
        return self.CULTIVAR_INFO.get(crop, [])
    
    async def get_species_info(self, crop: str) -> Optional[Dict[str, Any]]:
        """
        Get species information for a crop.
        
        Args:
            crop: Crop name
            
        Returns:
            Species information or None
        """
        return self.SPECIES_INFO.get(crop)
    
    async def find_variable_synonyms(self, variable_code: str) -> List[str]:
        """
        Find synonyms for a variable code.
        
        Args:
            variable_code: Variable code
            
        Returns:
            List of synonym codes
        """
        return self.VARIABLE_SYNONYMS.get(variable_code, [])
    
    async def search_variables(self, query: str) -> List[Dict[str, Any]]:
        """
        Search variables by name or description.
        
        Args:
            query: Search query
            
        Returns:
            Matching variable definitions
        """
        results = []
        query_lower = query.lower()
        
        for code, info in self.VARIABLE_DEFINITIONS.items():
            if (query_lower in code.lower() or 
                query_lower in info["full_name"].lower() or
                query_lower in info["description"].lower()):
                results.append({"code": code, **info})
        
        return results
    
    async def get_all_variables(self) -> List[Dict[str, str]]:
        """
        Get all variable definitions.
        
        Returns:
            List of all variable definitions
        """
        return [
            {"code": code, **info}
            for code, info in self.VARIABLE_DEFINITIONS.items()
        ]
