"""
Google Sheets integration service
Handles all read/write operations with Google Sheets
Converts raw sheet data to structured domain models
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Tuple
import sys
from pathlib import Path
from datetime import datetime, date

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import GOOGLE_CREDENTIALS_PATH, SHEET_NAME, SHEET_ID, USE_MOCK_DATA
from models.pilot import Pilot
from models.drone import Drone
from models.mission import Mission


class SheetsService:
    """Service for Google Sheets operations"""
    
    def __init__(self):
        """Initialize Google Sheets client"""
        self.client = None
        self.spreadsheet = None
        self.use_mock = USE_MOCK_DATA
        
        if not self.use_mock:
            try:
                self._authenticate()
            except Exception as e:
                print(f"⚠️ Google Sheets authentication failed: {e}")
                print("⚠️ Falling back to mock data mode")
                self.use_mock = True
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        # Define scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Load credentials
        credentials = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH, 
            scopes=scopes
        )
        
        # Create client
        self.client = gspread.authorize(credentials)
        print(f"✅ Successfully authenticated with Google Sheets")
        
        # Open spreadsheet by ID or name
        if SHEET_ID:
            self.spreadsheet = self.client.open_by_key(SHEET_ID)
            print(f"✅ Opened spreadsheet by ID: {SHEET_ID}")
        else:
            self.spreadsheet = self.client.open(SHEET_NAME)
            print(f"✅ Opened spreadsheet: {SHEET_NAME}")
    
    def get_worksheet(self, sheet_name: str):
        """Get worksheet by name"""
        if self.use_mock:
            return None
        
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except Exception as e:
            print(f"❌ Error opening worksheet '{sheet_name}': {e}")
            return None
    
    def _get_mock_pilots(self) -> List[Pilot]:
        """Return mock pilot data for testing"""
        return [
            Pilot(
                name="Raj Kumar",
                location="Delhi",
                skills=["Thermal Imaging", "LiDAR"],
                certifications=["DGCA Level 2", "Advanced Operations"],
                status="Available",
                daily_rate=5000.0
            ),
            Pilot(
                name="Priya Singh",
                location="Mumbai",
                skills=["Aerial Photography", "Video"],
                certifications=["DGCA Level 1"],
                status="Available",
                daily_rate=4000.0
            ),
            Pilot(
                name="Anand Verma",
                location="Bangalore",
                skills=["Thermal Imaging", "GIS"],
                certifications=["DGCA Level 2"],
                status="On Leave",
                daily_rate=6000.0
            ),
        ]
    
    def _get_mock_drones(self) -> List[Drone]:
        """Return mock drone data for testing"""
        return [
            Drone(
                id="DJI-001",
                name="Phantom 4 Pro",
                location="Delhi",
                status="Available",
                capability="Thermal Imaging",
                weather_rating="IP67",
                maintenance_hours=0
            ),
            Drone(
                id="DJI-002",
                name="Matrice 300 RTK",
                location="Mumbai",
                status="Available",
                capability="LiDAR",
                weather_rating="IP45",
                maintenance_hours=0
            ),
            Drone(
                id="DJI-003",
                name="Air 2S",
                location="Bangalore",
                status="Maintenance",
                capability="Aerial Photography",
                weather_rating="IP54",
                maintenance_hours=24
            ),
        ]
    
    def _get_mock_missions(self) -> List[Mission]:
        """Return mock mission data for testing"""
        return [
            Mission(
                id="M001",
                name="Dam Inspection",
                location="Delhi",
                start_date=date(2026, 2, 20),
                end_date=date(2026, 2, 22),
                required_skills=["Thermal Imaging"],
                required_certifications=["DGCA Level 2"],
                budget=50000.0,
                priority="High",
                status="Unassigned",
                assigned_pilot=None,
                assigned_drone=None
            ),
            Mission(
                id="M002",
                name="Site Survey",
                location="Mumbai",
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 3),
                required_skills=["Aerial Photography"],
                required_certifications=["DGCA Level 1"],
                budget=35000.0,
                priority="Medium",
                status="Unassigned",
                assigned_pilot=None,
                assigned_drone=None
            ),
        ]
    
    def read_pilots(self) -> List[Pilot]:
        """Read all pilots from Pilots sheet"""
        if self.use_mock:
            print("📋 Using mock pilot data")
            return self._get_mock_pilots()
        
        try:
            worksheet = self.get_worksheet("Pilots")
            if not worksheet:
                return self._get_mock_pilots()
            
            records = worksheet.get_all_records()
            
            pilots = []
            for record in records:
                if record.get("Name"):  # Skip empty rows
                    pilot = Pilot.from_sheet_row(record)
                    pilots.append(pilot)
            
            print(f"✅ Read {len(pilots)} pilots from Sheets")
            return pilots
            
        except Exception as e:
            print(f"❌ Error reading pilots: {e}")
            print("📋 Falling back to mock data")
            return self._get_mock_pilots()
    
    def read_drones(self) -> List[Drone]:
        """Read all drones from Drones sheet"""
        if self.use_mock:
            print("📋 Using mock drone data")
            return self._get_mock_drones()
        
        try:
            worksheet = self.get_worksheet("Drones")
            if not worksheet:
                return self._get_mock_drones()
            
            records = worksheet.get_all_records()
            
            drones = []
            for record in records:
                if record.get("ID"):  # Skip empty rows
                    drone = Drone.from_sheet_row(record)
                    drones.append(drone)
            
            print(f"✅ Read {len(drones)} drones from Sheets")
            return drones
            
        except Exception as e:
            print(f"❌ Error reading drones: {e}")
            print("📋 Falling back to mock data")
            return self._get_mock_drones()
    
    def read_missions(self) -> List[Mission]:
        """Read all missions from Missions sheet"""
        if self.use_mock:
            print("📋 Using mock mission data")
            return self._get_mock_missions()
        
        try:
            worksheet = self.get_worksheet("Missions")
            if not worksheet:
                return self._get_mock_missions()
            
            records = worksheet.get_all_records()
            
            missions = []
            for record in records:
                if record.get("ID"):  # Skip empty rows
                    mission = Mission.from_sheet_row(record)
                    missions.append(mission)
            
            print(f"✅ Read {len(missions)} missions from Sheets")
            return missions
            
        except Exception as e:
            print(f"❌ Error reading missions: {e}")
            print("📋 Falling back to mock data")
            return self._get_mock_missions()
    
    def update_pilot_status(self, name: str, new_status: str) -> bool:
        """Update pilot status in Pilots sheet"""
        if self.use_mock:
            print(f"📝 [MOCK] Updated {name} status to {new_status}")
            return True
        
        try:
            worksheet = self.get_worksheet("Pilots")
            if not worksheet:
                return False
            
            records = worksheet.get_all_records()
            
            # Find pilot row
            for idx, record in enumerate(records):
                if record.get("Name") == name:
                    # Update status (row number is idx + 2, because row 1 is headers)
                    worksheet.update_cell(idx + 2, 5, new_status)  # Assuming Status is column 5
                    print(f"✅ Updated {name} status to {new_status}")
                    return True
            
            print(f"❌ Pilot '{name}' not found")
            return False
            
        except Exception as e:
            print(f"❌ Error updating pilot status: {e}")
            return False
    
    def update_drone_status(self, drone_id: str, new_status: str) -> bool:
        """Update drone status in Drones sheet"""
        if self.use_mock:
            print(f"📝 [MOCK] Updated drone {drone_id} status to {new_status}")
            return True
        
        try:
            worksheet = self.get_worksheet("Drones")
            if not worksheet:
                return False
            
            records = worksheet.get_all_records()
            
            # Find drone row
            for idx, record in enumerate(records):
                if record.get("ID") == drone_id:
                    # Update status (row number is idx + 2)
                    worksheet.update_cell(idx + 2, 3, new_status)  # Assuming Status is column 3
                    print(f"✅ Updated drone {drone_id} status to {new_status}")
                    return True
            
            print(f"❌ Drone '{drone_id}' not found")
            return False
            
        except Exception as e:
            print(f"❌ Error updating drone status: {e}")
            return False
    
    def assign_mission(self, mission_id: str, pilot_name: Optional[str], drone_id: Optional[str]) -> bool:
        """Assign pilot and drone to mission"""
        if self.use_mock:
            print(f"📝 [MOCK] Mission {mission_id} assigned to {pilot_name}/{drone_id}")
            return True
        
        try:
            worksheet = self.get_worksheet("Missions")
            if not worksheet:
                return False
            
            records = worksheet.get_all_records()
            
            # Find mission row
            for idx, record in enumerate(records):
                if record.get("ID") == mission_id:
                    row_num = idx + 2
                    # Update Assigned Pilot and Assigned Drone columns
                    if pilot_name:
                        worksheet.update_cell(row_num, 9, pilot_name)  # Column 9
                    if drone_id:
                        worksheet.update_cell(row_num, 10, drone_id)  # Column 10
                    # Update status to Assigned
                    worksheet.update_cell(row_num, 8, "Assigned")
                    print(f"✅ Mission {mission_id} assigned to {pilot_name}/{drone_id}")
                    return True
            
            print(f"❌ Mission '{mission_id}' not found")
            return False
            
        except Exception as e:
            print(f"❌ Error assigning mission: {e}")
            return False
    
    def get_all_data(self) -> Tuple[List[Pilot], List[Drone], List[Mission]]:
        """
        Load all data in one call (pilots, drones, missions)
        Returns structured domain models
        
        Returns:
            Tuple of (pilots, drones, missions)
        """
        pilots = self.read_pilots()
        drones = self.read_drones()
        missions = self.read_missions()
        return pilots, drones, missions
    
    def get_pilot_by_name(self, name: str) -> Optional[Pilot]:
        """Find pilot by name"""
        pilots = self.read_pilots()
        for pilot in pilots:
            if pilot.name.lower() == name.lower():
                return pilot
        return None
    
    def get_drone_by_id(self, drone_id: str) -> Optional[Drone]:
        """Find drone by ID"""
        drones = self.read_drones()
        for drone in drones:
            if drone.id == drone_id:
                return drone
        return None
    
    def get_mission_by_id(self, mission_id: str) -> Optional[Mission]:
        """Find mission by ID"""
        missions = self.read_missions()
        for mission in missions:
            if mission.id == mission_id:
                return mission
        return None
    
    def get_available_pilots(self) -> List[Pilot]:
        """Get all available pilots"""
        pilots = self.read_pilots()
        return [p for p in pilots if p.is_available()]
    
    def get_available_drones(self) -> List[Drone]:
        """Get all available drones"""
        drones = self.read_drones()
        return [d for d in drones if d.is_available()]
    
    def get_unassigned_missions(self) -> List[Mission]:
        """Get all unassigned missions"""
        missions = self.read_missions()
        return [m for m in missions if m.is_unassigned()]
    
    def get_pilots_by_location(self, location: str) -> List[Pilot]:
        """Get all pilots in a specific location"""
        pilots = self.read_pilots()
        return [p for p in pilots if p.location.lower() == location.lower()]
    
    def get_drones_by_location(self, location: str) -> List[Drone]:
        """Get all drones in a specific location"""
        drones = self.read_drones()
        return [d for d in drones if d.location.lower() == location.lower()]
    
    def get_pilots_with_skill(self, skill: str) -> List[Pilot]:
        """Get all pilots with specific skill"""
        pilots = self.read_pilots()
        return [p for p in pilots if skill in p.skills]
    
    def get_pilots_with_certification(self, certification: str) -> List[Pilot]:
        """Get all pilots with specific certification"""
        pilots = self.read_pilots()
        return [p for p in pilots if certification in p.certifications]
    
    def get_drones_with_capability(self, capability: str) -> List[Drone]:
        """Get all drones with specific capability"""
        drones = self.read_drones()
        return [d for d in drones if d.capability.lower() == capability.lower()]
    
    def validate_assignment(self, pilot: Pilot, drone: Drone, mission: Mission) -> Tuple[bool, str]:
        """
        Validate if assignment is valid (helper for conflict detection)
        
        Returns:
            Tuple (is_valid, error_message)
        """
        # Check pilot status
        if not pilot.is_available():
            return False, f"❌ Pilot {pilot.name} is {pilot.status}"
        
        # Check drone status
        if not drone.is_available():
            return False, f"❌ Drone {drone.id} is {drone.status}"
        
        # Check location match (optional - could be flexible)
        if pilot.location != mission.location and drone.location != mission.location:
            return False, f"❌ Neither pilot nor drone in mission location {mission.location}"
        
        # Check skills
        if not pilot.has_all_skills(mission.required_skills):
            return False, f"❌ Pilot missing required skills"
        
        # Check certifications
        if not pilot.has_all_certifications(mission.required_certifications):
            return False, f"❌ Pilot missing required certifications"
        
        return True, "✅ Assignment valid"
    
    def get_data_stats(self) -> Dict:
        """Get statistics about loaded data"""
        pilots = self.read_pilots()
        drones = self.read_drones()
        missions = self.read_missions()
        
        return {
            "total_pilots": len(pilots),
            "available_pilots": len([p for p in pilots if p.is_available()]),
            "total_drones": len(drones),
            "available_drones": len([d for d in drones if d.is_available()]),
            "total_missions": len(missions),
            "unassigned_missions": len([m for m in missions if m.is_unassigned()]),
            "assigned_missions": len([m for m in missions if m.is_assigned()]),
            "mode": "MOCK" if self.use_mock else "REAL_SHEETS"
        }
