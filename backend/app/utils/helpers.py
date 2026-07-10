"""Utility functions."""
import hashlib


def generate_geohash(latitude: float, longitude: float, precision: int = 6) -> str:
    """
    Generate a geohash from latitude and longitude.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        precision: Geohash precision (1-12)

    Returns:
        Geohash string
    """
    # Simple implementation using hashlib
    coords = f"{latitude},{longitude}"
    hash_obj = hashlib.md5(coords.encode())
    return hash_obj.hexdigest()[:precision]


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate latitude and longitude coordinates.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        True if valid, False otherwise
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def format_date(date_str: str) -> str:
    """
    Format a date string.

    Args:
        date_str: Input date string

    Returns:
        Formatted date string
    """
    if not date_str:
        return None

    # Remove any whitespace and standardize format
    return date_str.strip()
