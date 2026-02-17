"""
Urgent Reassignment Service
Handles automatic reassignment of high-priority missions when conflicts occur
Integrates ConflictEngine, DecisionEngine, and AssignmentManager
"""

from typing import Optional, Dict, List
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.mission import Mission
from models.pilot import Pilot
from models.drone import Drone
from agent.conflict_engine import ConflictEngine
from agent.decision_engine import DecisionEngine
from agent.assignment_manager import AssignmentManager
from services.sheets_service import SheetsService


class UrgentReassignmentService:
    """Service for handling urgent reassignment of high-priority missions"""
    
    def __init__(self, sheets_service: Optional[SheetsService] = None):
        """Initialize urgent reassignment service"""
        self.sheets_service = sheets_service or SheetsService()
        self.conflict_engine = ConflictEngine()
        self.decision_engine = DecisionEngine()
        self.assignment_manager = AssignmentManager()
        self.reassignment_log = []
    
    def check_mission_validity(self, mission: Mission, pilots: List[Pilot], drones: List[Drone]) -> Dict:
        """
        Check if current mission assignment is still valid
        
        Returns:
            {
                "valid": bool,
                "conflicts": list,
                "reason": str
            }
        """
        # If mission is not assigned, it's valid (waiting for assignment)
        if mission.is_unassigned():
            return {
                "valid": True,
                "conflicts": [],
                "reason": "Mission is unassigned (not yet assigned)"
            }
        
        # Get assigned pilot and drone
        assigned_pilot = next((p for p in pilots if p.name == mission.assigned_pilot), None)
        assigned_drone = next((d for d in drones if d.drone_id == mission.assigned_drone), None)
        
        if not assigned_pilot or not assigned_drone:
            return {
                "valid": False,
                "conflicts": ["MISSING_PILOT" if not assigned_pilot else "MISSING_DRONE"],
                "reason": f"Assigned resource not found: pilot={assigned_pilot}, drone={assigned_drone}"
            }
        
        # Check pilot validity
        pilot_conflicts = self.conflict_engine.check_pilot_assignment(assigned_pilot, mission)
        pilot_valid = len(pilot_conflicts) == 0
        
        # Check drone validity
        drone_conflicts = self.conflict_engine.check_drone_assignment(assigned_drone, mission)
        drone_valid = len(drone_conflicts) == 0
        
        all_conflicts = pilot_conflicts + drone_conflicts
        
        return {
            "valid": pilot_valid and drone_valid,
            "conflicts": all_conflicts,
            "reason": f"Pilot valid: {pilot_valid}, Drone valid: {drone_valid}"
        }
    
    def handle_urgent_mission(self, mission_id: str, pilots: List[Pilot], drones: List[Drone], missions: List[Mission]) -> Dict:
        """
        Main handler for urgent reassignment of high-priority missions
        
        Flow:
        1. Load mission
        2. Check if high priority
        3. Check current assignment validity
        4. If invalid, find next best candidate and reassign
        5. Update sheets
        6. Log event
        
        Returns:
            {
                "status": "NO_ACTION" | "REASSIGNED" | "UNASSIGNABLE",
                "mission_id": str,
                "priority": str,
                "previous_pilot": str,
                "previous_drone": str,
                "new_pilot": str,
                "new_drone": str,
                "conflicts": list,
                "reason": str,
                "timestamp": str
            }
        """
        print(f"\n🔥 URGENT REASSIGNMENT CHECK for mission {mission_id}")
        
        # Load mission
        mission = next((m for m in missions if m.project_id == mission_id), None)
        if not mission:
            return {
                "status": "ERROR",
                "mission_id": mission_id,
                "reason": f"Mission {mission_id} not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check if high or urgent priority
        if mission.priority.lower() not in ["high", "urgent"]:
            return {
                "status": "NO_ACTION",
                "mission_id": mission_id,
                "priority": mission.priority,
                "reason": "Mission is not high or urgent priority - urgent reassignment not required",
                "conflicts": [],
                "timestamp": datetime.now().isoformat()
            }
        
        print(f"📌 High-priority mission detected: {mission.project_id} ({mission.client})")
        
        # Check current assignment validity
        validity_check = self.check_mission_validity(mission, pilots, drones)
        
        if validity_check["valid"]:
            print(f"✅ Current assignment is valid - no reassignment needed")
            return {
                "status": "NO_ACTION",
                "mission_id": mission_id,
                "priority": mission.priority,
                "assigned_pilot": mission.assigned_pilot,
                "assigned_drone": mission.assigned_drone,
                "reason": validity_check["reason"],
                "conflicts": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Invalid assignment detected - need to reassign
        print(f"⚠️ CONFLICT DETECTED: {validity_check['reason']}")
        print(f"   Conflicts: {', '.join(validity_check['conflicts'])}")
        
        # Store previous assignment
        previous_pilot = mission.assigned_pilot
        previous_drone = mission.assigned_drone
        
        # Get available pilots and drones
        available_pilots = self.assignment_manager.get_available_pilots(mission, pilots)
        available_drones = self.assignment_manager.get_available_drones(mission, drones)
        
        print(f"   Available pilots: {len(available_pilots)}")
        print(f"   Available drones: {len(available_drones)}")
        
        if not available_pilots or not available_drones:
            result = {
                "status": "UNASSIGNABLE",
                "mission_id": mission_id,
                "priority": mission.priority,
                "previous_pilot": previous_pilot,
                "previous_drone": previous_drone,
                "reason": f"No available pilots ({len(available_pilots)}) or drones ({len(available_drones)})",
                "conflicts": validity_check["conflicts"],
                "timestamp": datetime.now().isoformat()
            }
            self.reassignment_log.append(result)
            return result
        
        # Use DecisionEngine to find best assignment
        best_assignment = self.decision_engine.find_best_assignment(
            mission=mission,
            pilots=available_pilots,
            drones=available_drones
        )
        
        if not best_assignment:
            result = {
                "status": "UNASSIGNABLE",
                "mission_id": mission_id,
                "priority": mission.priority,
                "previous_pilot": previous_pilot,
                "previous_drone": previous_drone,
                "reason": "DecisionEngine found no suitable assignment",
                "conflicts": validity_check["conflicts"],
                "timestamp": datetime.now().isoformat()
            }
            self.reassignment_log.append(result)
            return result
        
        # Extract new assignment
        new_pilot = best_assignment.get("pilot")
        new_drone = best_assignment.get("drone")
        
        if not new_pilot or not new_drone:
            result = {
                "status": "UNASSIGNABLE",
                "mission_id": mission_id,
                "priority": mission.priority,
                "previous_pilot": previous_pilot,
                "previous_drone": previous_drone,
                "reason": "DecisionEngine returned incomplete assignment",
                "conflicts": validity_check["conflicts"],
                "timestamp": datetime.now().isoformat()
            }
            self.reassignment_log.append(result)
            return result
        
        scores = {
            "pilot_score": best_assignment.get("pilot_score", 0),
            "drone_score": best_assignment.get("drone_score", 0),
            "combined_score": best_assignment.get("total_score", 0)
        }
        
        print(f"✅ Found alternative assignment:")
        print(f"   New Pilot: {new_pilot.name} (score: {scores.get('pilot_score', 'N/A')})")
        print(f"   New Drone: {new_drone.drone_id} (score: {scores.get('drone_score', 'N/A')})")
        
        # Update mission assignment
        try:
            # Use AssignmentManager to update
            new_mission = Mission(
                project_id=mission.project_id,
                client=mission.client,
                location=mission.location,
                start_date=mission.start_date,
                end_date=mission.end_date,
                required_skills=mission.required_skills,
                required_certs=mission.required_certs,
                mission_budget_inr=mission.mission_budget_inr,
                priority=mission.priority,
                status="Assigned",
                assigned_pilot=new_pilot.name,
                assigned_drone=new_drone.drone_id,
                weather_forecast=mission.weather_forecast
            )
            
            update_result = self.assignment_manager.reassign_mission(
                mission=new_mission,
                pilot=new_pilot,
                drone=new_drone
            )
            
            # Update Google Sheets
            print(f"📝 Updating Google Sheets...")
            sheets_success = self.sheets_service.assign_mission(
                mission_id=mission_id,
                pilot_name=new_pilot.name,
                drone_id=new_drone.drone_id
            )
            
            if not sheets_success:
                print(f"⚠️ Failed to update sheets, but assignment manager updated")
            
            # Log successful reassignment
            result = {
                "status": "REASSIGNED",
                "mission_id": mission_id,
                "priority": mission.priority,
                "previous_pilot": previous_pilot,
                "previous_drone": previous_drone,
                "new_pilot": new_pilot.name,
                "new_drone": new_drone.drone_id,
                "pilot_score": scores.get("pilot_score", 0),
                "drone_score": scores.get("drone_score", 0),
                "combined_score": scores.get("combined_score", 0),
                "conflicts_resolved": validity_check["conflicts"],
                "reason": f"Reassigned due to: {', '.join(validity_check['conflicts'])}",
                "timestamp": datetime.now().isoformat()
            }
            
            self.reassignment_log.append(result)
            print(f"🎉 REASSIGNMENT COMPLETE")
            return result
            
        except Exception as e:
            result = {
                "status": "ERROR",
                "mission_id": mission_id,
                "priority": mission.priority,
                "previous_pilot": previous_pilot,
                "previous_drone": previous_drone,
                "reason": f"Exception during reassignment: {str(e)}",
                "conflicts": validity_check["conflicts"],
                "timestamp": datetime.now().isoformat()
            }
            self.reassignment_log.append(result)
            print(f"❌ Error: {str(e)}")
            return result
    
    def handle_all_high_priority_missions(self, pilots: List[Pilot], drones: List[Drone], missions: List[Mission]) -> Dict:
        """
        Check and reassign ALL high-priority missions
        
        Returns:
            {
                "total_checked": int,
                "reassigned": int,
                "unassignable": int,
                "no_action": int,
                "errors": int,
                "results": list
            }
        """
        print(f"\n{'='*60}")
        print(f"🔥 URGENT REASSIGNMENT SCAN - ALL HIGH PRIORITY MISSIONS")
        print(f"{'='*60}")
        
        high_priority_missions = [m for m in missions if m.priority.lower() == "high"]
        
        if not high_priority_missions:
            print(f"ℹ️ No high-priority missions found")
            return {
                "total_checked": 0,
                "reassigned": 0,
                "unassignable": 0,
                "no_action": 0,
                "errors": 0,
                "results": []
            }
        
        print(f"Found {len(high_priority_missions)} high-priority missions\n")
        
        results = []
        for mission in high_priority_missions:
            result = self.handle_urgent_mission(
                mission_id=mission.project_id,
                pilots=pilots,
                drones=drones,
                missions=missions
            )
            results.append(result)
        
        # Summarize
        reassigned = len([r for r in results if r.get("status") == "REASSIGNED"])
        unassignable = len([r for r in results if r.get("status") == "UNASSIGNABLE"])
        no_action = len([r for r in results if r.get("status") == "NO_ACTION"])
        errors = len([r for r in results if r.get("status") == "ERROR"])
        
        print(f"\n{'='*60}")
        print(f"📊 URGENT REASSIGNMENT SUMMARY")
        print(f"{'='*60}")
        print(f"Total checked:   {len(high_priority_missions)}")
        print(f"Reassigned:      {reassigned} ✅")
        print(f"No action:       {no_action} ℹ️")
        print(f"Unassignable:    {unassignable} ⚠️")
        print(f"Errors:          {errors} ❌")
        print(f"{'='*60}\n")
        
        return {
            "total_checked": len(high_priority_missions),
            "reassigned": reassigned,
            "unassignable": unassignable,
            "no_action": no_action,
            "errors": errors,
            "results": results
        }
    
    def get_reassignment_log(self) -> List[Dict]:
        """Get all reassignment events"""
        return self.reassignment_log
    
    def clear_log(self):
        """Clear reassignment log"""
        self.reassignment_log = []
