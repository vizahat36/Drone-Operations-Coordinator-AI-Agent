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
    """Mission data model with Google Sheets fields"""
    project_id: str
    client: str
    location: str
    start_date: date
    end_date: date
    required_skills: list
    required_certs: list
    mission_budget_inr: float
    priority: str  # High, Medium, Low
    status: str  # Unassigned, Assigned, InProgress, Completed
    assigned_pilot: Optional[str] = None
    assigned_drone: Optional[str] = None
    weather_forecast: Optional[str] = None  # Weather conditions for mission
    
    @classmethod
    def from_sheet_row(cls, row: dict):
        """Create Mission from Google Sheet row with safe parsing"""
        start_date = parse_date(row.get("start_date", ""))
        end_date = parse_date(row.get("end_date", ""))
        
        return cls(
            project_id=parse_string(row.get("project_id", "")),
            client=parse_string(row.get("client", "")),
            location=parse_string(row.get("location", "")),
            start_date=start_date,
            end_date=end_date,
            required_skills=parse_list_field(row.get("required_skills", "")),
            required_certs=parse_list_field(row.get("required_certs", "")),
            mission_budget_inr=parse_float(row.get("mission_budget_inr", 0)),
            priority=parse_string(row.get("priority", "Medium")),
            status=parse_string(row.get("status", "Unassigned")),
            assigned_pilot=parse_string(row.get("assigned_pilot", "")),
            assigned_drone=parse_string(row.get("assigned_drone", "")),
            weather_forecast=parse_string(row.get("weather_forecast", ""))
        )
    
    def to_dict(self):
        """Convert to dictionary with Google Sheets column names"""
        return {
            "project_id": self.project_id,
            "client": self.client,
            "location": self.location,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "required_skills": ", ".join(self.required_skills),
            "required_certs": ", ".join(self.required_certs),
            "mission_budget_inr": self.mission_budget_inr,
            "priority": self.priority,
            "status": self.status,
            "assigned_pilot": self.assigned_pilot or "",
            "assigned_drone": self.assigned_drone or "",
            "weather_forecast": self.weather_forecast or ""
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
