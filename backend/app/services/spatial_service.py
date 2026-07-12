"""Spatial Service - location-based filtering and analysis."""
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geoalchemy2 import functions as geo_func
from geoalchemy2 import WKTElement
from sqlalchemy import and_, text

from app.models.simulation import Simulation
from app.repositories.simulation import SimulationRepository

logger = logging.getLogger(__name__)


class SpatialService:
    """Service for spatial queries."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.sim_repo = SimulationRepository(db)
    
    async def search_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int,
        crop: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search simulations within radius.
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_meters: Radius in meters
            crop: Filter by crop (optional)
            limit: Maximum results
            
        Returns:
            List of simulations within radius
        """
        # Convert meters to degrees (approximate)
        radius_deg = radius_meters / 111000.0
        
        stmt = select(Simulation).where(
            and_(
                Simulation.latitude >= latitude - radius_deg,
                Simulation.latitude <= latitude + radius_deg,
                Simulation.longitude >= longitude - radius_deg,
                Simulation.longitude <= longitude + radius_deg
            )
        ).limit(limit)
        
        if crop:
            stmt = stmt.where(Simulation.crop == crop)
        
        result = await self.db.execute(stmt)
        simulations = result.scalars().all()
        
        return [self._simulation_to_dict(sim) for sim in simulations]
    
    async def search_by_polygon(
        self,
        polygon_wkt: str,
        crop: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search simulations within polygon.
        
        Args:
            polygon_wkt: Polygon in WKT format
            crop: Filter by crop (optional)
            limit: Maximum results
            
        Returns:
            List of simulations within polygon
        """
        polygon_geom = WKTElement(polygon_wkt, srid=4326)
        
        stmt = select(Simulation).where(
            geo_func.ST_Within(Simulation.location, polygon_geom)
        ).limit(limit)
        
        if crop:
            stmt = stmt.where(Simulation.crop == crop)
        
        result = await self.db.execute(stmt)
        simulations = result.scalars().all()
        
        return [self._simulation_to_dict(sim) for sim in simulations]
    
    async def search_by_country(
        self,
        country: str,
        state: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search by country (and optionally state/district).
        
        Args:
            country: Country name
            state: State name (optional)
            district: District name (optional)
            limit: Maximum results
            
        Returns:
            List of simulations
        """
        stmt = select(Simulation).where(
            Simulation.country == country
        ).limit(limit)
        
        if state:
            stmt = stmt.where(Simulation.state == state)
        
        if district:
            stmt = stmt.where(Simulation.district == district)
        
        result = await self.db.execute(stmt)
        simulations = result.scalars().all()
        
        return [self._simulation_to_dict(sim) for sim in simulations]
    
    async def search_by_state(
        self,
        state: str,
        crop: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search by state.
        
        Args:
            state: State name
            crop: Filter by crop (optional)
            limit: Maximum results
            
        Returns:
            List of simulations
        """
        stmt = select(Simulation).where(
            Simulation.state == state
        ).limit(limit)
        
        if crop:
            stmt = stmt.where(Simulation.crop == crop)
        
        result = await self.db.execute(stmt)
        simulations = result.scalars().all()
        
        return [self._simulation_to_dict(sim) for sim in simulations]
    
    async def search_by_district(
        self,
        district: str,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search by district.
        
        Args:
            district: District name
            state: State name (optional)
            limit: Maximum results
            
        Returns:
            List of simulations
        """
        stmt = select(Simulation).where(
            Simulation.district == district
        ).limit(limit)
        
        if state:
            stmt = stmt.where(Simulation.state == state)
        
        result = await self.db.execute(stmt)
        simulations = result.scalars().all()
        
        return [self._simulation_to_dict(sim) for sim in simulations]
    
    async def search_by_ecological_zone(
        self,
        ecological_zone: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search by ecological zone.
        
        Args:
            ecological_zone: Ecological zone name
            limit: Maximum results
            
        Returns:
            List of simulations
        """
        stmt = select(Simulation).where(
            Simulation.ecological_zone == ecological_zone
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        simulations = result.scalars().all()
        
        return [self._simulation_to_dict(sim) for sim in simulations]
    
    async def get_bounds(self, crop: Optional[str] = None) -> Dict[str, float]:
        """
        Get bounding box of all simulations.
        
        Args:
            crop: Filter by crop (optional)
            
        Returns:
            Dictionary with min/max lat/lon
        """
        from sqlalchemy import func
        
        stmt = select(
            func.min(Simulation.latitude).label("min_lat"),
            func.max(Simulation.latitude).label("max_lat"),
            func.min(Simulation.longitude).label("min_lon"),
            func.max(Simulation.longitude).label("max_lon")
        )
        
        if crop:
            stmt = stmt.where(Simulation.crop == crop)
        
        result = await self.db.execute(stmt)
        row = result.fetchone()
        
        return {
            "min_lat": row.min_lat,
            "max_lat": row.max_lat,
            "min_lon": row.min_lon,
            "max_lon": row.max_lon
        }
    
    async def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two points in meters.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        # Haversine formula approximation
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Earth radius in meters
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _simulation_to_dict(self, sim: Simulation) -> Dict[str, Any]:
        """Convert simulation to dictionary."""
        return {
            "simulation_id": str(sim.simulation_id),
            "experiment_name": sim.experiment_name,
            "run_name": sim.run_name,
            "country": sim.country,
            "state": sim.state,
            "district": sim.district,
            "latitude": sim.latitude,
            "longitude": sim.longitude,
            "crop": sim.crop,
            "cultivar": sim.cultivar,
            "simulation_year": sim.simulation_year
        }
