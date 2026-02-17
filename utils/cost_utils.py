"""
Cost calculation utilities
Handles pilot cost, mission budget validation, and financial calculations
"""

from datetime import date
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_parser import calculate_duration_days


def calculate_pilot_cost(daily_rate: float, mission_duration_days: int) -> float:
    """
    Calculate total cost for pilot assignment.
    
    Formula: cost = daily_rate × mission_duration
    
    Args:
        daily_rate: Pilot's daily rate in currency
        mission_duration_days: Number of days for mission
        
    Returns:
        Total cost
        
    Example:
        >>> calculate_pilot_cost(5000, 3)
        15000
    """
    if daily_rate < 0 or mission_duration_days < 0:
        return 0.0
    
    return daily_rate * mission_duration_days


def calculate_mission_cost_estimate(
    pilot_daily_rate: float,
    start_date: date,
    end_date: date
) -> float:
    """
    Calculate estimated mission cost based on dates.
    
    Args:
        pilot_daily_rate: Pilot's daily rate
        start_date: Mission start date
        end_date: Mission end date
        
    Returns:
        Estimated cost
    """
    duration = calculate_duration_days(start_date, end_date)
    return calculate_pilot_cost(pilot_daily_rate, duration)


def is_within_budget(mission_budget: float, required_cost: float) -> bool:
    """
    Check if required cost is within mission budget.
    
    Args:
        mission_budget: Mission's allocated budget
        required_cost: Required cost for assignment
        
    Returns:
        True if within budget, False otherwise
    """
    if mission_budget < 0 or required_cost < 0:
        return False
    
    return required_cost <= mission_budget


def get_budget_remaining(mission_budget: float, used_cost: float) -> float:
    """
    Calculate remaining budget.
    
    Args:
        mission_budget: Total mission budget
        used_cost: Already used cost
        
    Returns:
        Remaining budget (can be negative)
    """
    return mission_budget - used_cost


def is_budget_critical(mission_budget: float, used_cost: float, threshold_percent: float = 80.0) -> bool:
    """
    Check if budget usage exceeds critical threshold.
    
    Args:
        mission_budget: Total mission budget
        used_cost: Already used cost
        threshold_percent: Critical threshold percentage (default 80%)
        
    Returns:
        True if budget usage >= threshold, False otherwise
    """
    if mission_budget <= 0:
        return False
    
    used_percent = (used_cost / mission_budget) * 100
    return used_percent >= threshold_percent


def compare_pilot_costs(pilots_with_costs: list) -> list:
    """
    Sort pilots by cost (ascending).
    
    Args:
        pilots_with_costs: List of tuples: (pilot, cost)
        
    Returns:
        Sorted list by cost (cheapest first)
    """
    return sorted(pilots_with_costs, key=lambda x: x[1])


def find_most_cost_effective_pilot(pilots_with_costs: list) -> Optional[tuple]:
    """
    Find the most cost-effective pilot.
    
    Args:
        pilots_with_costs: List of tuples: (pilot, cost)
        
    Returns:
        Tuple (pilot, cost) or None if list is empty
    """
    if not pilots_with_costs:
        return None
    
    sorted_pilots = compare_pilot_costs(pilots_with_costs)
    return sorted_pilots[0]
