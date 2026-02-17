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
        
        # Debug prints
        print(f"🔧 USE_MOCK_DATA from .env: {USE_MOCK_DATA}")
        print(f"🔧 Final mode: {'MOCK' if self.use_mock else 'REAL'}")
        
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
    
    def _get_column_index(self, worksheet, column_name: str) -> int:
        """Get column index by header name (1-based)"""
        try:
            # Get header row using get_all_values()[0]
            headers = worksheet.get_all_values()[0]
            
            # Normalize headers: strip whitespace and convert to lowercase
            normalized_headers = [h.strip().lower() for h in headers]
            
            # Normalize target column name
            target = column_name.strip().lower()
            
            # Check if column exists
            if target not in normalized_headers:
                raise ValueError(f"Column '{column_name}' not found in headers: {[h.strip() for h in headers]}")
            
            # Get 1-based index for gspread
            col_index = normalized_headers.index(target) + 1
            print(f"✅ Column '{column_name}' → Index {col_index}")
            return col_index
            
        except ValueError as e:
            print(f"❌ {str(e)}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error getting column index for '{column_name}': {e}")
            raise

    def _ensure_columns(self, worksheet, required_columns: List[str]) -> Dict[str, int]:
        """Ensure columns exist in the header row and return their indices (1-based)."""
        try:
            all_values = worksheet.get_all_values()
            headers = all_values[0] if all_values else []
        except Exception:
            headers = []

        normalized = [h.strip().lower() for h in headers]

        for column_name in required_columns:
            if column_name.strip().lower() not in normalized:
                headers.append(column_name)
                normalized.append(column_name.strip().lower())
                worksheet.update_cell(1, len(headers), column_name)

        return {
            column_name: normalized.index(column_name.strip().lower()) + 1
            for column_name in required_columns
        }
    
    def _get_mock_pilots(self) -> List[Pilot]:
        """Return mock pilot data for testing"""
        return [
            Pilot(
                pilot_id="P001",
                name="Raj Kumar",
                location="Delhi",
                skills=["Thermal Imaging", "LiDAR"],
                certifications=["DGCA Level 2", "Advanced Operations"],
                status="Available",
                daily_rate_inr=5000.0
            ),
            Pilot(
                pilot_id="P002",
                name="Priya Singh",
                location="Mumbai",
                skills=["Aerial Photography", "Video"],
                certifications=["DGCA Level 1"],
                status="Available",
                daily_rate_inr=4000.0
            ),
            Pilot(
                pilot_id="P003",
                name="Anand Verma",
                location="Bangalore",
                skills=["Thermal Imaging", "GIS"],
                certifications=["DGCA Level 2"],
                status="On Leave",
                daily_rate_inr=6000.0
            ),
        ]
    
    def _get_mock_drones(self) -> List[Drone]:
        """Return mock drone data for testing"""
        return [
            Drone(
                drone_id="DJI-001",
                model="Phantom 4 Pro",
                location="Delhi",
                status="Available",
                capabilities="Thermal Imaging",
                weather_resistance="IP67",
                maintenance_due=0
            ),
            Drone(
                drone_id="DJI-002",
                model="Matrice 300 RTK",
                location="Mumbai",
                status="Available",
                capabilities="LiDAR",
                weather_resistance="IP45",
                maintenance_due=0
            ),
            Drone(
                drone_id="DJI-003",
                model="Air 2S",
                location="Bangalore",
                status="Maintenance",
                capabilities="Aerial Photography",
                weather_resistance="IP54",
                maintenance_due=24
            ),
        ]
    
    def _get_mock_missions(self) -> List[Mission]:
        """Return mock mission data for testing"""
        return [
            Mission(
                project_id="M001",
                client="Dam Inspection",
                location="Delhi",
                start_date=date(2026, 2, 20),
                end_date=date(2026, 2, 22),
                required_skills=["Thermal Imaging"],
                required_certs=["DGCA Level 2"],
                mission_budget_inr=50000.0,
                priority="High",
                status="Unassigned",
                assigned_pilot=None,
                assigned_drone=None
            ),
            Mission(
                project_id="M002",
                client="Site Survey",
                location="Mumbai",
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 3),
                required_skills=["Aerial Photography"],
                required_certs=["DGCA Level 1"],
                mission_budget_inr=35000.0,
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
                raise RuntimeError("Worksheet 'Pilots' not found. Not using mock in REAL mode.")
            
            records = worksheet.get_all_records()
            
            pilots = []
            for record in records:
                if record.get("name"):  # Skip empty rows
                    pilot = Pilot.from_sheet_row(record)
                    pilots.append(pilot)
            
            print(f"✅ Read {len(pilots)} pilots from Sheets")
            return pilots
            
        except Exception as e:
            print(f"❌ Error reading pilots: {e}")
            raise RuntimeError(f"Failed to read pilots from Google Sheets in REAL mode: {e}")
    
    def read_drones(self) -> List[Drone]:
        """Read all drones from Drones sheet"""
        if self.use_mock:
            print("📋 Using mock drone data")
            return self._get_mock_drones()
        
        try:
            worksheet = self.get_worksheet("Drones")
            if not worksheet:
                raise RuntimeError("Worksheet 'Drones' not found. Not using mock in REAL mode.")
            
            records = worksheet.get_all_records()
            
            drones = []
            for record in records:
                if record.get("drone_id"):  # Skip empty rows
                    drone = Drone.from_sheet_row(record)
                    drones.append(drone)
            
            print(f"✅ Read {len(drones)} drones from Sheets")
            return drones
            
        except Exception as e:
            print(f"❌ Error reading drones: {e}")
            raise RuntimeError(f"Failed to read drones from Google Sheets in REAL mode: {e}")
    
    def read_missions(self) -> List[Mission]:
        """Read all missions from Missions sheet"""
        if self.use_mock:
            print("📋 Using mock mission data")
            return self._get_mock_missions()
        
        try:
            worksheet = self.get_worksheet("Missions")
            if not worksheet:
                raise RuntimeError("Worksheet 'Missions' not found. Not using mock in REAL mode.")
            
            records = worksheet.get_all_records()
            
            missions = []
            for record in records:
                if record.get("project_id"):  # Skip empty rows
                    mission = Mission.from_sheet_row(record)
                    missions.append(mission)
            
            print(f"✅ Read {len(missions)} missions from Sheets")
            return missions
            
        except Exception as e:
            print(f"❌ Error reading missions: {e}")
            raise RuntimeError(f"Failed to read missions from Google Sheets in REAL mode: {e}")
    
    def update_pilot_status_detail(self, name: str, new_status: str) -> Tuple[bool, str]:
        """Update pilot status in Pilots sheet with detailed failure reason."""
        if self.use_mock:
            print(f"📝 [MOCK] Updated {name} status to {new_status}")
            return True, "Updated in mock mode"
        
        try:
            worksheet = self.get_worksheet("Pilots")
            if not worksheet:
                return False, "Pilots worksheet not found"
            
            # Get Status column index dynamically (raises ValueError if not found)
            status_col = self._get_column_index(worksheet, "Status")
            
            records = worksheet.get_all_records()
            
            # Find pilot row
            for idx, record in enumerate(records):
                if record.get("name") == name:
                    # Update status (row number is idx + 2, because row 1 is headers)
                    worksheet.update_cell(idx + 2, status_col, new_status)
                    print(f"✅ Updated {name} status to {new_status} (column {status_col})")
                    return True, "Pilot status updated"
            
            print(f"❌ Pilot '{name}' not found")
            return False, f"Pilot '{name}' not found"
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            print(f"❌ Error updating pilot status: {e}")
            return False, f"Error updating pilot status: {e}"

    def update_pilot_status(self, name: str, new_status: str) -> bool:
        """Update pilot status in Pilots sheet"""
        success, _ = self.update_pilot_status_detail(name, new_status)
        return success
    
    def update_drone_status_detail(self, drone_id: str, new_status: str) -> Tuple[bool, str]:
        """Update drone status in Drones sheet with detailed failure reason."""
        if self.use_mock:
            print(f"📝 [MOCK] Updated drone {drone_id} status to {new_status}")
            return True, "Updated in mock mode"
        
        try:
            worksheet = self.get_worksheet("Drones")
            if not worksheet:
                return False, "Drones worksheet not found"
            
            # Get Status column index dynamically (raises ValueError if not found)
            status_col = self._get_column_index(worksheet, "Status")
            
            records = worksheet.get_all_records()
            
            # Find drone row
            for idx, record in enumerate(records):
                if record.get("drone_id") == drone_id:
                    # Update status (row number is idx + 2)
                    worksheet.update_cell(idx + 2, status_col, new_status)
                    print(f"✅ Updated drone {drone_id} status to {new_status} (column {status_col})")
                    return True, "Drone status updated"
            
            print(f"❌ Drone '{drone_id}' not found")
            return False, f"Drone '{drone_id}' not found"
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            print(f"❌ Error updating drone status: {e}")
            return False, f"Error updating drone status: {e}"

    def update_drone_status(self, drone_id: str, new_status: str) -> bool:
        """Update drone status in Drones sheet"""
        success, _ = self.update_drone_status_detail(drone_id, new_status)
        return success
    
    def assign_mission_detail(self, mission_id: str, pilot_name: Optional[str], drone_id: Optional[str]) -> Tuple[bool, str]:
        """Assign pilot and drone to mission with detailed failure reason."""
        if self.use_mock:
            print(f"📝 [MOCK] Mission {mission_id} assigned to {pilot_name}/{drone_id}")
            return True, "Assigned in mock mode"
        
        try:
            worksheet = self.get_worksheet("Missions")
            if not worksheet:
                return False, "Missions worksheet not found"
            
            # Ensure mission assignment columns exist
            columns = self._ensure_columns(
                worksheet,
                ["status", "assigned_pilot", "assigned_drone"]
            )
            status_col = columns.get("status")
            pilot_col = columns.get("assigned_pilot")
            drone_col = columns.get("assigned_drone")
            
            records = worksheet.get_all_records()
            
            # Find mission row
            for idx, record in enumerate(records):
                if record.get("project_id") == mission_id:
                    row_num = idx + 2
                    
                    # Update Assigned Pilot column if exists
                    if pilot_name and pilot_col:
                        worksheet.update_cell(row_num, pilot_col, pilot_name)
                    
                    # Update Assigned Drone column if exists
                    if drone_id and drone_col:
                        worksheet.update_cell(row_num, drone_col, drone_id)
                    
                    # Update status to Assigned if column exists
                    if status_col:
                        worksheet.update_cell(row_num, status_col, "Assigned")
                    
                    print(f"✅ Mission {mission_id} assigned to {pilot_name}/{drone_id} (columns: status={status_col}, pilot={pilot_col}, drone={drone_col})")
                    
                    # Also update current_assignment in Pilots and Drones sheets if present
                    if pilot_name:
                        pilots_ws = self.get_worksheet("Pilots")
                        if pilots_ws:
                            try:
                                pilot_assign_col = self._get_column_index(pilots_ws, "current_assignment")
                                pilot_records = pilots_ws.get_all_records()
                                for p_idx, p_record in enumerate(pilot_records):
                                    if p_record.get("name") == pilot_name:
                                        pilots_ws.update_cell(p_idx + 2, pilot_assign_col, mission_id)
                                        break
                            except ValueError:
                                print(f"⚠️ 'current_assignment' column not found in Pilots sheet, skipping pilot assignment update")
                    
                    if drone_id:
                        drones_ws = self.get_worksheet("Drones")
                        if drones_ws:
                            try:
                                drone_assign_col = self._get_column_index(drones_ws, "current_assignment")
                                drone_records = drones_ws.get_all_records()
                                for d_idx, d_record in enumerate(drone_records):
                                    if d_record.get("drone_id") == drone_id:
                                        drones_ws.update_cell(d_idx + 2, drone_assign_col, mission_id)
                                        break
                            except ValueError:
                                print(f"⚠️ 'current_assignment' column not found in Drones sheet, skipping drone assignment update")
                    
                    return True, "Mission assigned"
            
            print(f"❌ Mission '{mission_id}' not found")
            return False, f"Mission '{mission_id}' not found"
            
        except Exception as e:
            print(f"❌ Error assigning mission: {e}")
            return False, f"Error assigning mission: {e}"

    def assign_mission(self, mission_id: str, pilot_name: Optional[str], drone_id: Optional[str]) -> bool:
        """Assign pilot and drone to mission"""
        success, _ = self.assign_mission_detail(mission_id, pilot_name, drone_id)
        return success
    
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
            if drone.drone_id == drone_id:
                return drone
        return None
    
    def get_mission_by_id(self, mission_id: str) -> Optional[Mission]:
        """Find mission by ID"""
        missions = self.read_missions()
        for mission in missions:
            if mission.project_id == mission_id:
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
        return [d for d in drones if d.capabilities.lower() == capability.lower()]
    
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
            return False, f"❌ Drone {drone.drone_id} is {drone.status}"
        
        # Check location match (optional - could be flexible)
        if pilot.location != mission.location and drone.location != mission.location:
            return False, f"❌ Neither pilot nor drone in mission location {mission.location}"
        
        # Check skills
        if not pilot.has_all_skills(mission.required_skills):
            return False, f"❌ Pilot missing required skills"
        
        # Check certifications
        if not pilot.has_all_certifications(mission.required_certs):
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
