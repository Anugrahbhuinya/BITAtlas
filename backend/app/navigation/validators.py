# backend/app/navigation/validators.py

from typing import Dict, Any, List

def validate_coordinates(lat: float, lng: float) -> bool:
    """
    Validates that latitude is within [-90, 90] and longitude is within [-180, 180].
    Further validates that the coordinate lies in the proximity of BIT Mesra (optional, but good for sanity checks).
    """
    if not (-90.0 <= lat <= 90.0):
        return False
    if not (-180.0 <= lng <= 180.0):
        return False
    return True

def validate_entrance(entrance: Dict[str, Any]) -> bool:
    """
    Validates building entrance structure.
    """
    if "name" not in entrance or not entrance["name"]:
        return False
    if "latitude" not in entrance or not isinstance(entrance["latitude"], (int, float)):
        return False
    if "longitude" not in entrance or not isinstance(entrance["longitude"], (int, float)):
        return False
    return validate_coordinates(entrance["latitude"], entrance["longitude"])

def validate_accessibility(accessibility: Dict[str, Any]) -> bool:
    """
    Validates building or facility accessibility object fields.
    """
    required_keys = ["wheelchair_accessible"]
    for key in required_keys:
        if key not in accessibility:
            return False
    return True
