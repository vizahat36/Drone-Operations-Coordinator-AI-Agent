"""
Conflict Detection Engine
Identifies scheduling conflicts, skill mismatches, budget issues, and other constraints
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.pilot import Pilot
from models.drone import Drone
from models.mission import Mission
from utils.data_parser import dates_overlap
from utils.cost_utils import calculate_pilot_cost, is_within_budget


class ConflictEngine:
    """
    Detects conflicts and constraints that prevent pilot/drone assignment
    
    Conflict Types:
    1. Double-booking (date overlap)
    2. Skill mismatch
    3. Certification mismatch
    4. Budget overrun
    5. Status unavailability
    6. Weather incompatibility
    7. Location mismatch
    8. Maintenance conflicts
    """
    
    def __init__(self):
        """Initialize conflict engine"""
        self.conflicts = []
    
    # ===== PILOT CONFLICTS =====
    
    def check_pilot_availability(self, pilot: Pilot) -> Optional[Dict]:
        """Check if pilot is available (Available status)"""
        if not pilot.is_available():
            return {
                "type": "AVAILABILITY",
                "severity": "CRITICAL",
                "message": f"Pilot {pilot.name} is {pilot.status}",
                "pilot": pilot.name,
                "code": "PILOT_NOT_AVAILABLE"
            }
        return None
    
    def check_skills_match(self, pilot: Pilot, mission: Mission) -> Optional[Dict]:
        """Check if pilot has all required skills"""
        missing_skills = [s for s in mission.required_skills if s not in pilot.skills]
        
        if missing_skills:
            return {
                "type": "SKILLS",
                "severity": "CRITICAL",
                "message": f"Pilot {pilot.name} missing skills: {missing_skills}",
                "pilot": pilot.name,
                "mission": mission.id,
                "missing": missing_skills,
                "code": "SKILL_MISMATCH"
            }
        return None
    
    def check_certifications_match(self, pilot: Pilot, mission: Mission) -> Optional[Dict]:
        """Check if pilot has all required certifications"""
        missing_certs = [c for c in mission.required_certifications 
                        if c not in pilot.certifications]
        
        if missing_certs:
            return {
                "type": "CERTIFICATIONS",
                "severity": "CRITICAL",
                "message": f"Pilot {pilot.name} missing certs: {missing_certs}",
                "pilot": pilot.name,
                "mission": mission.id,
                "missing": missing_certs,
                "code": "CERT_MISMATCH"
            }
        return None
    
    def check_pilot_budget(self, pilot: Pilot, mission: Mission) -> Optional[Dict]:
        """Check if pilot cost exceeds mission budget"""
        duration = (mission.end_date - mission.start_date).days + 1
        cost = calculate_pilot_cost(pilot.daily_rate, duration)
        
        if not is_within_budget(mission.budget, cost):
            budget_ratio = (cost / mission.budget) * 100
            return {
                "type": "BUDGET",
                "severity": "HIGH",
                "message": f"Pilot {pilot.name} costs ₹{cost}, mission budget ₹{mission.budget}",
                "pilot": pilot.name,
                "mission": mission.id,
                "cost": cost,
                "budget": mission.budget,
                "overage": cost - mission.budget,
                "overage_percent": round(budget_ratio - 100, 2),
                "code": "BUDGET_OVERRUN"
            }
        return None
    
    def check_date_overlap(self, pilot: Pilot, mission: Mission, 
                          other_missions: Optional[List[Mission]] = None) -> Optional[Dict]:
        """Check if pilot has schedule conflict with other assignments"""
        if not other_missions:
            return None
        
        conflicts = []
        for other_mission in other_missions:
            if other_mission.id == mission.id:
                continue  # Skip same mission
            
            if dates_overlap(mission.start_date, mission.end_date,
                           other_mission.start_date, other_mission.end_date):
                conflicts.append({
                    "mission_id": other_mission.id,
                    "mission_name": other_mission.name,
                    "start": str(other_mission.start_date),
                    "end": str(other_mission.end_date)
                })
        
        if conflicts:
            return {
                "type": "DOUBLE_BOOKING",
                "severity": "CRITICAL",
                "message": f"Pilot {pilot.name} has schedule conflicts",
                "pilot": pilot.name,
                "mission": mission.id,
                "conflicts": conflicts,
                "code": "DATE_OVERLAP"
            }
        return None
    
    def check_location_mismatch(self, pilot: Pilot, mission: Mission) -> Optional[Dict]:
        """Check location mismatch (warning, not critical)"""
        if pilot.location != mission.location:
            return {
                "type": "LOCATION",
                "severity": "WARNING",
                "message": f"Pilot in {pilot.location}, mission in {mission.location}",
                "pilot": pilot.name,
                "pilot_location": pilot.location,
                "mission_location": mission.location,
                "code": "LOCATION_MISMATCH"
            }
        return None
    
    # ===== DRONE CONFLICTS =====
    
    def check_drone_availability(self, drone: Drone) -> Optional[Dict]:
        """Check if drone is available"""
        if not drone.is_available():
            return {
                "type": "AVAILABILITY",
                "severity": "CRITICAL",
                "message": f"Drone {drone.id} is {drone.status}",
                "drone": drone.id,
                "code": "DRONE_NOT_AVAILABLE"
            }
        return None
    
    def check_drone_maintenance(self, drone: Drone, mission: Mission) -> Optional[Dict]:
        """Check if drone maintenance conflicts with mission"""
        if drone.maintenance_hours > 0:
            return {
                "type": "MAINTENANCE",
                "severity": "HIGH",
                "message": f"Drone {drone.id} requires {drone.maintenance_hours}h maintenance",
                "drone": drone.id,
                "maintenance_hours": drone.maintenance_hours,
                "code": "MAINTENANCE_REQUIRED"
            }
        return None
    
    def check_drone_date_overlap(self, drone: Drone, mission: Mission,
                                other_missions: Optional[List[Mission]] = None) -> Optional[Dict]:
        """Check if drone has schedule conflict"""
        if not other_missions:
            return None
        
        conflicts = []
        for other_mission in other_missions:
            if other_mission.id == mission.id:
                continue
            
            if dates_overlap(mission.start_date, mission.end_date,
                           other_mission.start_date, other_mission.end_date):
                conflicts.append({
                    "mission_id": other_mission.id,
                    "mission_name": other_mission.name,
                    "start": str(other_mission.start_date),
                    "end": str(other_mission.end_date)
                })
        
        if conflicts:
            return {
                "type": "DOUBLE_BOOKING",
                "severity": "CRITICAL",
                "message": f"Drone {drone.id} has schedule conflicts",
                "drone": drone.id,
                "mission": mission.id,
                "conflicts": conflicts,
                "code": "DRONE_DATE_OVERLAP"
            }
        return None
    
    def check_weather_compatibility(self, drone: Drone, mission: Mission) -> Optional[Dict]:
        """Check weather compatibility (simplified)"""
        # In real system, would check against weather forecast
        # For now, simplified check
        return None
    
    # ===== COMPREHENSIVE CHECKS =====
    
    def check_pilot_assignment(self, pilot: Pilot, mission: Mission, 
                              other_missions: Optional[List[Mission]] = None) -> List[Dict]:
        """
        Check all conflicts for pilot assignment to mission
        
        Returns:
            List of conflicts (empty if valid)
        """
        conflicts = []
        
        # Critical checks (blocking)
        availability = self.check_pilot_availability(pilot)
        if availability:
            conflicts.append(availability)
            return conflicts  # Stop if not available
        
        skills = self.check_skills_match(pilot, mission)
        if skills:
            conflicts.append(skills)
        
        certs = self.check_certifications_match(pilot, mission)
        if certs:
            conflicts.append(certs)
        
        budget = self.check_pilot_budget(pilot, mission)
        if budget:
            conflicts.append(budget)
        
        overlap = self.check_date_overlap(pilot, mission, other_missions)
        if overlap:
            conflicts.append(overlap)
        
        # Warnings (non-blocking)
        location = self.check_location_mismatch(pilot, mission)
        if location:
            conflicts.append(location)
        
        return conflicts
    
    def check_drone_assignment(self, drone: Drone, mission: Mission,
                              other_missions: Optional[List[Mission]] = None) -> List[Dict]:
        """
        Check all conflicts for drone assignment to mission
        
        Returns:
            List of conflicts (empty if valid)
        """
        conflicts = []
        
        # Critical checks
        availability = self.check_drone_availability(drone)
        if availability:
            conflicts.append(availability)
            return conflicts
        
        maintenance = self.check_drone_maintenance(drone, mission)
        if maintenance:
            conflicts.append(maintenance)
        
        overlap = self.check_drone_date_overlap(drone, mission, other_missions)
        if overlap:
            conflicts.append(overlap)
        
        # Warnings
        weather = self.check_weather_compatibility(drone, mission)
        if weather:
            conflicts.append(weather)
        
        return conflicts
    
    def generate_conflict_report(self, mission: Mission, pilots: List[Pilot], 
                                drones: List[Drone],
                                other_missions: Optional[List[Mission]] = None) -> Dict:
        """
        Generate comprehensive conflict report for mission
        
        Returns:
            Report with all conflicts grouped by type
        """
        report = {
            "mission_id": mission.id,
            "mission_name": mission.name,
            "timestamp": str(Path(__file__).stat().st_mtime),
            "pilot_analysis": {},
            "drone_analysis": {},
            "summary": {
                "total_pilots": len(pilots),
                "total_drones": len(drones),
                "viable_pilots": 0,
                "viable_drones": 0,
                "critical_blocks": 0,
                "warnings": 0
            }
        }
        
        # Analyze pilots
        for pilot in pilots:
            conflicts = self.check_pilot_assignment(pilot, mission, other_missions)
            report["pilot_analysis"][pilot.name] = {
                "viable": len(conflicts) == 0,
                "conflicts": conflicts
            }
            if not conflicts:
                report["summary"]["viable_pilots"] += 1
            
            # Count critical vs warnings
            for conflict in conflicts:
                if conflict["severity"] == "CRITICAL":
                    report["summary"]["critical_blocks"] += 1
                else:
                    report["summary"]["warnings"] += 1
        
        # Analyze drones
        for drone in drones:
            conflicts = self.check_drone_assignment(drone, mission, other_missions)
            report["drone_analysis"][drone.id] = {
                "viable": len(conflicts) == 0,
                "conflicts": conflicts
            }
            if not conflicts:
                report["summary"]["viable_drones"] += 1
            
            for conflict in conflicts:
                if conflict["severity"] == "CRITICAL":
                    report["summary"]["critical_blocks"] += 1
                else:
                    report["summary"]["warnings"] += 1
        
        return report
