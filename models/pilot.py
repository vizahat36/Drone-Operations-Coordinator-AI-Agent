"""
Pilot data model
"""

from dataclasses import dataclass
from typing import List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_parser import parse_list_field, parse_string, parse_float


@dataclass
class Pilot:
    """Pilot data model with Google Sheets fields"""
    pilot_id: str
    name: str
    location: str
    skills: List[str]
    certifications: List[str]
    status: str  # Available, On Leave, Unavailable
    current_assignment: Optional[str] = None  # Current mission ID if assigned
    available_from: Optional[str] = None  # Date when pilot becomes available
    daily_rate_inr: float = 0.0
    
    @classmethod
    def from_sheet_row(cls, row: dict):
        """Create Pilot from Google Sheet row with safe parsing"""
        return cls(
            pilot_id=parse_string(row.get("pilot_id", "")),
            name=parse_string(row.get("name", "")),
            location=parse_string(row.get("location", "")),
            skills=parse_list_field(row.get("skills", "")),
            certifications=parse_list_field(row.get("certifications", "")),
            status=parse_string(row.get("status", "Available")),
            current_assignment=parse_string(row.get("current_assignment", "")),
            available_from=parse_string(row.get("available_from", "")),
            daily_rate_inr=parse_float(row.get("daily_rate_inr", 0))
        )
    
    def to_dict(self):
        """Convert to dictionary with Google Sheets column names"""
        return {
            "pilot_id": self.pilot_id,
            "name": self.name,
            "location": self.location,
            "skills": ", ".join(self.skills),
            "certifications": ", ".join(self.certifications),
            "status": self.status,
            "current_assignment": self.current_assignment or "",
            "available_from": self.available_from or "",
            "daily_rate_inr": self.daily_rate_inr
        }
    
    def has_all_skills(self, required_skills: List[str]) -> bool:
        """Check if pilot has all required skills"""
        return all(skill in self.skills for skill in required_skills)
    
    def has_all_certifications(self, required_certs: List[str]) -> bool:
        """Check if pilot has all required certifications"""
        return all(cert in self.certifications for cert in required_certs)
    
    def is_available(self) -> bool:
        """Check if pilot is available"""
        return self.status == "Available"
