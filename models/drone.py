"""
Drone data model
"""

from dataclasses import dataclass
from typing import List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_parser import parse_string, parse_int


@dataclass
class Drone:
    """Drone data model"""
    id: str
    name: str
    location: str
    status: str  # Available, Deployed, Maintenance
    capability: str
    weather_rating: str  # e.g., IP20, IP67, Waterproof
    maintenance_hours: int
    
    @classmethod
    def from_sheet_row(cls, row: dict):
        """Create Drone from Google Sheet row with safe parsing"""
        return cls(
            id=parse_string(row.get("ID", "")),
            name=parse_string(row.get("Name", "")),
            location=parse_string(row.get("Location", "")),
            status=parse_string(row.get("Status", "Available")),
            capability=parse_string(row.get("Capability", "")),
            weather_rating=parse_string(row.get("Weather Rating", "IP20")),
            maintenance_hours=parse_int(row.get("Maintenance Hours", 0))
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "ID": self.id,
            "Name": self.name,
            "Location": self.location,
            "Status": self.status,
            "Capability": self.capability,
            "Weather Rating": self.weather_rating,
            "Maintenance Hours": self.maintenance_hours
        }
    
    def is_available(self) -> bool:
        """Check if drone is available"""
        return self.status == "Available"
    
    def is_in_maintenance(self) -> bool:
        """Check if drone is in maintenance"""
        return self.status == "Maintenance"
    
    def is_deployed(self) -> bool:
        """Check if drone is deployed"""
        return self.status == "Deployed"
