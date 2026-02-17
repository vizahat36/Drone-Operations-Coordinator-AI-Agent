"""
Mission data model
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_parser import (
    parse_string, parse_list_field, parse_float, parse_date,
    validate_date_range, dates_overlap, calculate_duration_days
)


@dataclass
class Mission:
    """Mission data model"""
    id: str
    name: str
    location: str
    start_date: date
    end_date: date
    required_skills: list
    required_certifications: list
    budget: float
    priority: str  # High, Medium, Low
    status: str  # Unassigned, Assigned, Completed
    assigned_pilot: Optional[str] = None
    assigned_drone: Optional[str] = None
    
    @classmethod
    def from_sheet_row(cls, row: dict):
        """Create Mission from Google Sheet row with safe parsing"""
        start_date = parse_date(row.get("Start Date", ""))
        end_date = parse_date(row.get("End Date", ""))
        
        return cls(
            id=parse_string(row.get("ID", "")),
            name=parse_string(row.get("Name", "")),
            location=parse_string(row.get("Location", "")),
            start_date=start_date,
            end_date=end_date,
            required_skills=parse_list_field(row.get("Required Skills", "")),
            required_certifications=parse_list_field(row.get("Required Certifications", "")),
            budget=parse_float(row.get("Budget", 0)),
            priority=parse_string(row.get("Priority", "Medium")),
            status=parse_string(row.get("Status", "Unassigned")),
            assigned_pilot=parse_string(row.get("Assigned Pilot", "")),
            assigned_drone=parse_string(row.get("Assigned Drone", ""))
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "ID": self.id,
            "Name": self.name,
            "Location": self.location,
            "Start Date": str(self.start_date),
            "End Date": str(self.end_date),
            "Required Skills": ", ".join(self.required_skills),
            "Required Certifications": ", ".join(self.required_certifications),
            "Budget": self.budget,
            "Priority": self.priority,
            "Status": self.status,
            "Assigned Pilot": self.assigned_pilot or "",
            "Assigned Drone": self.assigned_drone or ""
        }
    
    def is_valid_dates(self) -> bool:
        """Check if date range is valid"""
        return validate_date_range(self.start_date, self.end_date)
    
    def get_duration_days(self) -> int:
        """Get mission duration in days"""
        return calculate_duration_days(self.start_date, self.end_date)
    
    def overlaps_with(self, other_mission: "Mission") -> bool:
        """Check if mission overlaps with another mission"""
        return dates_overlap(
            self.start_date, self.end_date,
            other_mission.start_date, other_mission.end_date
        )
    
    def is_unassigned(self) -> bool:
        """Check if mission is unassigned"""
        return self.status == "Unassigned"
    
    def is_assigned(self) -> bool:
        """Check if mission is assigned"""
        return self.status == "Assigned"
    
    def is_high_priority(self) -> bool:
        """Check if mission is high priority"""
        return self.priority == "High"
