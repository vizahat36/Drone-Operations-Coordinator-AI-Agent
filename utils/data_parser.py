"""
Data normalization and parsing utilities
Converts raw sheet data into clean Python objects
"""

from datetime import datetime, date
from typing import List, Optional, Union


def parse_list_field(value: Union[str, list]) -> List[str]:
    """
    Convert comma-separated string to list of strings.
    
    Examples:
        "Thermal Imaging, LiDAR, GIS" → ["Thermal Imaging", "LiDAR", "GIS"]
        "" → []
        None → []
    
    Args:
        value: Comma-separated string or list
        
    Returns:
        List of strings, stripped of whitespace
    """
    if not value:
        return []
    
    if isinstance(value, list):
        return [str(v).strip() for v in value if v]
    
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    
    return []


def parse_date(date_str: Union[str, date]) -> Optional[date]:
    """
    Convert date string to date object.
    
    Supports multiple formats:
        - "2026-02-17" (ISO format)
        - "02/17/2026" (US format)
        - "17-02-2026" (D-M-Y format)
    
    Args:
        date_str: Date string in various formats or date object
        
    Returns:
        date object or None if parsing fails
    """
    if not date_str:
        return None
    
    # If already a date object, return it
    if isinstance(date_str, date):
        return date_str
    
    if isinstance(date_str, datetime):
        return date_str.date()
    
    date_str = str(date_str).strip()
    
    # Try different date formats
    formats = [
        "%Y-%m-%d",      # 2026-02-17
        "%m/%d/%Y",      # 02/17/2026
        "%d-%m-%Y",      # 17-02-2026
        "%d/%m/%Y",      # 17/02/2026
        "%Y/%m/%d",      # 2026/02/17
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.date()
        except ValueError:
            continue
    
    print(f"⚠️  Warning: Could not parse date '{date_str}'")
    return None


def parse_float(value: Union[str, int, float]) -> float:
    """
    Convert value to float safely.
    
    Examples:
        "5000.50" → 5000.5
        5000 → 5000.0
        "invalid" → 0.0
        None → 0.0
    
    Args:
        value: String, int, or float value
        
    Returns:
        Float value, 0.0 if conversion fails
    """
    if value is None or value == "":
        return 0.0
    
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"⚠️  Warning: Could not parse '{value}' as float, using 0.0")
        return 0.0


def parse_int(value: Union[str, int]) -> int:
    """
    Convert value to int safely.
    
    Args:
        value: String or int value
        
    Returns:
        Integer value, 0 if conversion fails
    """
    if value is None or value == "":
        return 0
    
    try:
        return int(value)
    except (ValueError, TypeError):
        print(f"⚠️  Warning: Could not parse '{value}' as int, using 0")
        return 0


def parse_string(value) -> str:
    """
    Convert value to string safely.
    
    Args:
        value: Any value
        
    Returns:
        String representation, empty string if None
    """
    if value is None:
        return ""
    return str(value).strip()


def parse_bool(value: Union[str, bool]) -> bool:
    """
    Convert value to boolean safely.
    
    True values: "true", "yes", "1", "on", True
    False values: "false", "no", "0", "off", False, ""
    
    Args:
        value: String or boolean value
        
    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ["true", "yes", "1", "on"]
    
    return bool(value)


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate that start_date <= end_date.
    
    Args:
        start_date: Mission start date
        end_date: Mission end date
        
    Returns:
        True if valid range, False otherwise
    """
    if not start_date or not end_date:
        return False
    
    return start_date <= end_date


def calculate_duration_days(start_date: date, end_date: date) -> int:
    """
    Calculate number of days between two dates.
    
    Args:
        start_date: Mission start date
        end_date: Mission end date
        
    Returns:
        Number of days (inclusive)
    """
    if not start_date or not end_date:
        return 0
    
    return (end_date - start_date).days + 1


def dates_overlap(start1: date, end1: date, start2: date, end2: date) -> bool:
    """
    Check if two date ranges overlap.
    
    Formula: (start1 <= end2) AND (start2 <= end1)
    
    Args:
        start1, end1: First date range
        start2, end2: Second date range
        
    Returns:
        True if ranges overlap, False otherwise
    """
    if not all([start1, end1, start2, end2]):
        return False
    
    return (start1 <= end2) and (start2 <= end1)
