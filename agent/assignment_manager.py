"""
Assignment Manager
Coordinates assignments across multiple missions, prevents double-booking at system level
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.pilot import Pilot
from models.drone import Drone
from models.mission import Mission
from agent.decision_engine import DecisionEngine
from agent.conflict_engine import ConflictEngine
from utils.data_parser import dates_overlap


class AssignmentManager:
    """
    Manages assignments across the system
    - Tracks current assignments
    - Prevents double-booking at manager level
    - Handles reassignments
    - Maintains assignment history
    """
    
    def __init__(self):
        """Initialize assignment manager"""
        self.assignments = {}  # mission_id -> {pilot: Pilot, drone: Drone, score: float}
        self.assignment_history = []  # Track all assignment changes
        self.decision_engine = DecisionEngine()
        self.conflict_engine = ConflictEngine()
    
    def get_assigned_missions(self, pilot: Pilot) -> List[Mission]:
        """Get all missions assigned to a pilot"""
        missions = []
        for mission_id, assignment in self.assignments.items():
            if assignment and assignment.get("pilot") == pilot:
                missions.append(assignment.get("mission"))
        return [m for m in missions if m]
    
    def get_assigned_missions_drone(self, drone: Drone) -> List[Mission]:
        """Get all missions assigned to a drone"""
        missions = []
        for mission_id, assignment in self.assignments.items():
            if assignment and assignment.get("drone") == drone:
                missions.append(assignment.get("mission"))
        return [m for m in missions if m]
    
    def get_pilot_schedule(self, pilot: Pilot) -> List[Tuple[datetime, datetime]]:
        """Get pilot's schedule (date ranges of assigned missions)"""
        missions = self.get_assigned_missions(pilot)
        return [(m.start_date, m.end_date) for m in missions]
    
    def get_drone_schedule(self, drone: Drone) -> List[Tuple[datetime, datetime]]:
        """Get drone's schedule (date ranges of assigned missions)"""
        missions = self.get_assigned_missions_drone(drone)
        return [(m.start_date, m.end_date) for m in missions]
    
    def is_pilot_available(self, pilot: Pilot, mission: Mission) -> bool:
        """Check if pilot can be assigned (no schedule conflict)"""
        assigned_missions = self.get_assigned_missions(pilot)
        
        for assigned_mission in assigned_missions:
            if dates_overlap(mission.start_date, mission.end_date,
                           assigned_mission.start_date, assigned_mission.end_date):
                return False
        
        return True
    
    def is_drone_available(self, drone: Drone, mission: Mission) -> bool:
        """Check if drone can be assigned (no schedule conflict)"""
        assigned_missions = self.get_assigned_missions_drone(drone)
        
        for assigned_mission in assigned_missions:
            if dates_overlap(mission.start_date, mission.end_date,
                           assigned_mission.start_date, assigned_mission.end_date):
                return False
        
        return True
    
    def get_available_pilots(self, mission: Mission, pilots: List[Pilot]) -> List[Pilot]:
        """Get pilots available for this mission (no schedule conflict)"""
        available = []
        for pilot in pilots:
            if self.is_pilot_available(pilot, mission):
                available.append(pilot)
        return available
    
    def get_available_drones(self, mission: Mission, drones: List[Drone]) -> List[Drone]:
        """Get drones available for this mission (no schedule conflict)"""
        available = []
        for drone in drones:
            if self.is_drone_available(drone, mission):
                available.append(drone)
        return available
    
    def assign_mission(self, mission: Mission, pilot: Pilot, drone: Drone) -> Dict:
        """
        Assign pilot and drone to mission
        
        Returns:
            Status dict with assignment details
        """
        # Validate assignment
        if not self.is_pilot_available(pilot, mission):
            return {
                "success": False,
                "reason": "Pilot schedule conflict",
                "mission": mission.id,
                "pilot": pilot.name
            }
        
        if not self.is_drone_available(drone, mission):
            return {
                "success": False,
                "reason": "Drone schedule conflict",
                "mission": mission.id,
                "drone": drone.id
            }
        
        # Perform assignment
        self.assignments[mission.id] = {
            "mission": mission,
            "pilot": pilot,
            "drone": drone,
            "assigned_at": datetime.now().isoformat(),
            "score": 0.0  # Can be updated with decision engine score
        }
        
        # Record in history
        self.assignment_history.append({
            "action": "ASSIGN",
            "mission_id": mission.id,
            "pilot": pilot.name,
            "drone": drone.id,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "mission": mission.id,
            "pilot": pilot.name,
            "drone": drone.id,
            "message": f"Successfully assigned {pilot.name} + {drone.id} to {mission.name}"
        }
    
    def unassign_mission(self, mission_id: str) -> Dict:
        """
        Unassign mission
        
        Returns:
            Status dict
        """
        if mission_id not in self.assignments:
            return {
                "success": False,
                "reason": "Mission not assigned",
                "mission": mission_id
            }
        
        assignment = self.assignments[mission_id]
        self.assignments[mission_id] = None
        
        # Record in history
        self.assignment_history.append({
            "action": "UNASSIGN",
            "mission_id": mission_id,
            "pilot": assignment.get("pilot", {}).name if assignment.get("pilot") else None,
            "drone": assignment.get("drone", {}).id if assignment.get("drone") else None,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "mission": mission_id,
            "message": f"Successfully unassigned mission {mission_id}"
        }
    
    def reassign_mission(self, mission: Mission, pilot: Pilot, 
                        drone: Drone) -> Dict:
        """
        Reassign mission to different pilot/drone
        
        Returns:
            Status dict with reassignment details
        """
        # Unassign if already assigned
        if mission.id in self.assignments:
            self.unassign_mission(mission.id)
        
        # Assign to new pilot/drone
        return self.assign_mission(mission, pilot, drone)
    
    def get_assignment(self, mission_id: str) -> Optional[Dict]:
        """Get current assignment for a mission"""
        return self.assignments.get(mission_id)
    
    def get_all_assignments(self) -> List[Dict]:
        """Get all current assignments"""
        return [a for a in self.assignments.values() if a]
    
    def find_best_assignment_for_mission(self, mission: Mission, 
                                        pilots: List[Pilot],
                                        drones: List[Drone]) -> Optional[Dict]:
        """
        Find best assignment for mission considering current assignments
        
        Returns:
            Best assignment dict or None if impossible
        """
        # Get available pilots/drones for this mission
        available_pilots = self.get_available_pilots(mission, pilots)
        available_drones = self.get_available_drones(mission, drones)
        
        if not available_pilots or not available_drones:
            return None
        
        # Use decision engine with available resources
        assigned_pilot_ids = [
            a.get("pilot").name for a in self.get_all_assignments()
            if a and a.get("pilot")
        ]
        assigned_drone_ids = [
            a.get("drone").id for a in self.get_all_assignments()
            if a and a.get("drone")
        ]
        
        return self.decision_engine.find_best_assignment(
            mission, available_pilots, available_drones,
            assigned_pilot_ids, assigned_drone_ids
        )
    
    def get_assignment_report(self) -> Dict:
        """
        Generate comprehensive assignment report
        
        Returns:
            Report with all assignments and statistics
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_assignments": 0,
            "assignments": [],
            "summary": {
                "assigned_missions": 0,
                "unassigned_missions": 0,
                "pilots_utilized": set(),
                "drones_utilized": set()
            }
        }
        
        for mission_id, assignment in self.assignments.items():
            if assignment:
                report["total_assignments"] += 1
                report["summary"]["assigned_missions"] += 1
                if assignment.get("pilot"):
                    report["summary"]["pilots_utilized"].add(assignment["pilot"].name)
                if assignment.get("drone"):
                    report["summary"]["drones_utilized"].add(assignment["drone"].id)
                
                report["assignments"].append({
                    "mission_id": mission_id,
                    "mission_name": assignment.get("mission").name if assignment.get("mission") else None,
                    "pilot": assignment.get("pilot").name if assignment.get("pilot") else None,
                    "drone": assignment.get("drone").id if assignment.get("drone") else None,
                    "assigned_at": assignment.get("assigned_at")
                })
        
        report["summary"]["pilots_utilized"] = list(report["summary"]["pilots_utilized"])
        report["summary"]["drones_utilized"] = list(report["summary"]["drones_utilized"])
        
        return report
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get assignment history (optionally limited to recent N)"""
        if limit:
            return self.assignment_history[-limit:]
        return self.assignment_history
