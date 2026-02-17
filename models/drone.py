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
    """Drone data model with Google Sheets fields"""
    drone_id: str
    model: str
    location: str
    status: str  # Available, Deployed, Maintenance
    capabilities: str
    weather_resistance: str  # e.g., IP20, IP67, Waterproof
    maintenance_due: int
    current_assignment: str = ""  # Current mission ID if assigned
    
    @classmethod
    def from_sheet_row(cls, row: dict):
        """Create Drone from Google Sheet row with safe parsing"""
        return cls(
            drone_id=parse_string(row.get("drone_id", "")),
            model=parse_string(row.get("model", "")),
            location=parse_string(row.get("location", "")),
            status=parse_string(row.get("status", "Available")),
            capabilities=parse_string(row.get("capabilities", "")),
            weather_resistance=parse_string(row.get("weather_resistance", "IP20")),
            maintenance_due=parse_int(row.get("maintenance_due", 0)),
            current_assignment=parse_string(row.get("current_assignment", ""))
        )
    
    def to_dict(self):
        """Convert to dictionary with Google Sheets column names"""
        return {
            "drone_id": self.drone_id,
            "model": self.model,
            "location": self.location,
            "status": self.status,
            "capabilities": self.capabilities,
            "weather_resistance": self.weather_resistance,
            "maintenance_due": self.maintenance_due,
            "current_assignment": self.current_assignment
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
    
    def supports_capability(self, required_capability: str) -> bool:
        """Check if drone supports required capability"""
        return required_capability.lower() in self.capabilities.lower()
