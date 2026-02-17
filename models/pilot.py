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
    """Pilot data model"""
    name: str
    location: str
    skills: List[str]
    certifications: List[str]
    status: str  # Available, On Leave, Unavailable
    daily_rate: float
    
    @classmethod
    def from_sheet_row(cls, row: dict):
        """Create Pilot from Google Sheet row with safe parsing"""
        return cls(
            name=parse_string(row.get("Name", "")),
            location=parse_string(row.get("Location", "")),
            skills=parse_list_field(row.get("Skills", "")),
            certifications=parse_list_field(row.get("Certifications", "")),
            status=parse_string(row.get("Status", "Available")),
            daily_rate=parse_float(row.get("Daily Rate", 0))
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "Name": self.name,
            "Location": self.location,
            "Skills": ", ".join(self.skills),
            "Certifications": ", ".join(self.certifications),
            "Status": self.status,
            "Daily Rate": self.daily_rate
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
