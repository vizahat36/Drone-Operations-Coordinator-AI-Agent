"""
Date and time utility functions
Handles date parsing, validation, and formatting
"""

from datetime import date, datetime, timedelta
from typing import Optional, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_parser import parse_date, validate_date_range, dates_overlap, calculate_duration_days


def is_past_date(check_date: date) -> bool:
    """
    Check if date is in the past.
    
    Args:
        check_date: Date to check
        
    Returns:
        True if date is before today, False otherwise
    """
    return check_date < date.today()


def is_future_date(check_date: date) -> bool:
    """
    Check if date is in the future.
    
    Args:
        check_date: Date to check
        
    Returns:
        True if date is after today, False otherwise
    """
    return check_date > date.today()


def is_today(check_date: date) -> bool:
    """
    Check if date is today.
    
    Args:
        check_date: Date to check
        
    Returns:
        True if date is today, False otherwise
    """
    return check_date == date.today()


def days_until(target_date: date) -> int:
    """
    Calculate days until target date (can be negative for past dates).
    
    Args:
        target_date: Target date
        
    Returns:
        Number of days until target (negative if in past)
    """
    return (target_date - date.today()).days


def days_since(past_date: date) -> int:
    """
    Calculate days since past date.
    
    Args:
        past_date: Past date
        
    Returns:
        Number of days since date.days
    """
    return (date.today() - past_date).days


def add_days(start_date: date, num_days: int) -> date:
    """
    Add days to a date.
    
    Args:
        start_date: Base date
        num_days: Number of days to add
        
    Returns:
        New date
    """
    return start_date + timedelta(days=num_days)


def subtract_days(start_date: date, num_days: int) -> date:
    """
    Subtract days from a date.
    
    Args:
        start_date: Base date
        num_days: Number of days to subtract
        
    Returns:
        New date
    """
    return start_date - timedelta(days=num_days)


def get_date_range(start_date: date, end_date: date) -> List[date]:
    """
    Generate list of all dates in a range.
    
    Args:
        start_date: Start of range
        end_date: End of range (inclusive)
        
    Returns:
        List of dates
    """
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current = add_days(current, 1)
    return dates


def format_date(date_obj: date, format_str: str = "%Y-%m-%d") -> str:
    """
    Format date to string.
    
    Args:
        date_obj: Date object
        format_str: Format string (default ISO: YYYY-MM-DD)
        
    Returns:
        Formatted date string
    """
    if not date_obj:
        return ""
    return date_obj.strftime(format_str)


def get_date_difference_in_weeks(start_date: date, end_date: date) -> int:
    """
    Get difference between dates in weeks.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Number of weeks
    """
    days = (end_date - start_date).days
    return days // 7


def get_date_difference_in_months(start_date: date, end_date: date) -> int:
    """
    Get approximate difference between dates in months.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Approximate number of months
    """
    days = (end_date - start_date).days
    return days // 30


def get_week_number(date_obj: date) -> int:
    """
    Get ISO week number of date.
    
    Args:
        date_obj: Date object
        
    Returns:
        Week number (1-53)
    """
    return date_obj.isocalendar()[1]


def get_weekday_name(date_obj: date) -> str:
    """
    Get weekday name of date.
    
    Args:
        date_obj: Date object
        
    Returns:
        Weekday name (Monday, Tuesday, etc.)
    """
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return weekdays[date_obj.weekday()]


def is_weekend(date_obj: date) -> bool:
    """
    Check if date is weekend (Saturday or Sunday).
    
    Args:
        date_obj: Date object
        
    Returns:
        True if weekend, False otherwise
    """
    return date_obj.weekday() >= 5


def get_business_days(start_date: date, end_date: date) -> int:
    """
    Count business days (Mon-Fri) in date range.
    
    Args:
        start_date: Start of range
        end_date: End of range
        
    Returns:
        Number of business days
    """
    business_days = 0
    current = start_date
    while current <= end_date:
        if not is_weekend(current):
            business_days += 1
        current = add_days(current, 1)
    return business_days
