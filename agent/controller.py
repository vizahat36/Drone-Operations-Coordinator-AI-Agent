"""
Orchestrator Controller
Coordinates decision engine, conflict engine, and assignment manager
Handles conversational requests and system-level decisions
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.pilot import Pilot
from models.drone import Drone
from models.mission import Mission
from services.sheets_service import SheetsService
from agent.decision_engine import DecisionEngine
from agent.conflict_engine import ConflictEngine
from agent.assignment_manager import AssignmentManager
from agent.urgent_reassignment import UrgentReassignmentService


class Controller:
    """
    Main orchestrator for the drone operations system
    
    Coordinates:
    1. Data retrieval (SheetsService)
    2. Assignment decisions (DecisionEngine)
    3. Conflict detection (ConflictEngine)
    4. Assignment tracking (AssignmentManager)
    """
    
    def __init__(self):
        """Initialize controller with all engines"""
        self.sheets_service = SheetsService()
        self.decision_engine = DecisionEngine()
        self.conflict_engine = ConflictEngine()
        self.assignment_manager = AssignmentManager()
        self.urgent_reassignment_service = UrgentReassignmentService(self.sheets_service)
        
        # Load initial data
        self.refresh_data()
    
    def refresh_data(self):
        """Load all data from Google Sheets (or mock)"""
        data = self.sheets_service.get_all_data()
        self.pilots = data[0]  # Access tuple index instead of dict
        self.drones = data[1]
        self.missions = data[2]

    
    # ===== MISSION ASSIGNMENT =====
    
    def process_mission_assignment(self, mission: Mission) -> Dict:
        """
        Process assignment for a single mission
        
        Workflow:
        1. Find best assignment candidates
        2. Check for conflicts if needed
        3. Assign if valid
        4. Report result
        
        Returns:
            Result dict with assignment or conflict details
        """
        result = {
            "mission_id": mission.id,
            "mission_name": mission.name,
            "status": "PENDING",
            "assignment": None,
            "conflicts": None,
            "message": ""
        }
        
        # Find best assignment
        best_assignment = self.assignment_manager.find_best_assignment_for_mission(
            mission, self.pilots, self.drones
        )
        
        if best_assignment and best_assignment.get("pilot") and best_assignment.get("drone"):
            # Perform assignment
            assign_result = self.assignment_manager.assign_mission(
                mission,
                best_assignment["pilot"],
                best_assignment["drone"]
            )
            
            if assign_result["success"]:
                result["status"] = "ASSIGNED"
                result["assignment"] = {
                    "pilot": best_assignment["pilot"].name,
                    "drone": best_assignment["drone"].id,
                    "cost": best_assignment.get("total_cost", 0),
                    "score": best_assignment.get("combined_score", 0)
                }
                result["message"] = assign_result["message"]
            else:
                result["status"] = "FAILED"
                result["message"] = assign_result["reason"]
        else:
            # Find conflicts
            conflicts = self.conflict_engine.generate_conflict_report(
                mission, self.pilots, self.drones, self.missions
            )
            
            result["status"] = "UNASSIGNABLE"
            result["conflicts"] = conflicts
            result["message"] = f"No valid assignment: {conflicts['summary']['critical_blocks']} critical blocks"
        
        return result
    
    def process_multiple_missions(self, mission_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Process assignments for multiple missions
        
        Returns:
            List of results for each mission
        """
        if mission_ids:
            missions = [m for m in self.missions if m.id in mission_ids]
        else:
            missions = [m for m in self.missions if m.is_unassigned()]
        
        results = []
        for mission in missions:
            result = self.process_mission_assignment(mission)
            results.append(result)
        
        return results
    
    # ===== CONFLICT ANALYSIS =====
    
    def analyze_mission_conflicts(self, mission: Mission) -> Dict:
        """
        Detailed conflict analysis for a mission
        
        Returns:
            Comprehensive conflict report
        """
        return self.conflict_engine.generate_conflict_report(
            mission, self.pilots, self.drones, self.missions
        )
    
    def analyze_pilot_conflicts(self, pilot: Pilot, mission: Mission) -> List[Dict]:
        """
        Check specific pilot for mission assignment conflicts
        
        Returns:
            List of conflict dicts (empty if no conflicts)
        """
        return self.conflict_engine.check_pilot_assignment(
            pilot, mission, self.missions
        )
    
    def analyze_drone_conflicts(self, drone: Drone, mission: Mission) -> List[Dict]:
        """
        Check specific drone for mission assignment conflicts
        
        Returns:
            List of conflict dicts (empty if no conflicts)
        """
        return self.conflict_engine.check_drone_assignment(
            drone, mission, self.missions
        )
    
    # ===== ASSIGNMENT RECOMMENDATIONS =====
    
    def get_assignment_recommendations(self, mission: Mission, 
                                      top_n: int = 5) -> Dict:
        """
        Get recommended pilot-drone combinations for mission
        
        Returns:
            Dict with top recommendations
        """
        available_pilots = self.assignment_manager.get_available_pilots(
            mission, self.pilots
        )
        available_drones = self.assignment_manager.get_available_drones(
            mission, self.drones
        )
        
        if not available_pilots or not available_drones:
            return {
                "mission_id": mission.id,
                "recommendations": [],
                "reason": "Insufficient available resources"
            }
        
        recommendations = self.decision_engine.rank_assignments(
            mission, available_pilots, available_drones, top_n
        )
        
        return {
            "mission_id": mission.id,
            "mission_name": mission.name,
            "recommendations": [
                {
                    "rank": idx + 1,
                    "pilot": r["pilot"].name,
                    "drone": r["drone"].id,
                    "cost": r.get("total_cost", 0),
                    "score": r.get("combined_score", 0)
                }
                for idx, r in enumerate(recommendations)
            ],
            "total": len(recommendations)
        }
    
    # ===== QUERY METHODS =====
    
    def get_pilot_availability(self, pilot: Pilot) -> Dict:
        """Get pilot's availability info"""
        return {
            "pilot": pilot.name,
            "status": pilot.status,
            "assigned_missions": len(
                self.assignment_manager.get_assigned_missions(pilot)
            ),
            "schedule": [
                {
                    "mission_id": m.id,
                    "start": str(m.start_date),
                    "end": str(m.end_date)
                }
                for m in self.assignment_manager.get_assigned_missions(pilot)
            ]
        }
    
    def get_drone_availability(self, drone: Drone) -> Dict:
        """Get drone's availability info"""
        return {
            "drone": drone.id,
            "status": drone.status,
            "assigned_missions": len(
                self.assignment_manager.get_assigned_missions_drone(drone)
            ),
            "schedule": [
                {
                    "mission_id": m.id,
                    "start": str(m.start_date),
                    "end": str(m.end_date)
                }
                for m in self.assignment_manager.get_assigned_missions_drone(drone)
            ]
        }
    
    def get_mission_status(self, mission: Mission) -> Dict:
        """Get mission status and assignment"""
        assignment = self.assignment_manager.get_assignment(mission.id)
        
        return {
            "mission_id": mission.id,
            "mission_name": mission.name,
            "status": "ASSIGNED" if assignment else "UNASSIGNED",
            "pilot": assignment["pilot"].name if assignment and assignment.get("pilot") else None,
            "drone": assignment["drone"].id if assignment and assignment.get("drone") else None,
            "priority": mission.priority,
            "start_date": str(mission.start_date),
            "end_date": str(mission.end_date),
            "budget": mission.budget
        }
    
    # ===== SYSTEM STATUS =====
    
    def get_system_status(self) -> Dict:
        """Get overall system status and statistics"""
        all_assignments = self.assignment_manager.get_all_assignments()
        
        assigned_missions = len(all_assignments)
        unassigned_missions = len([m for m in self.missions if m.is_unassigned()])
        
        return {
            "system_status": {
                "total_pilots": len(self.pilots),
                "available_pilots": len([p for p in self.pilots if p.is_available()]),
                "total_drones": len(self.drones),
                "available_drones": len([d for d in self.drones if d.is_available()]),
                "total_missions": len(self.missions),
                "assigned_missions": assigned_missions,
                "unassigned_missions": unassigned_missions
            },
            "recent_assignments": [
                {
                    "mission": a["mission"].name if a.get("mission") else None,
                    "pilot": a["pilot"].name if a.get("pilot") else None,
                    "drone": a["drone"].id if a.get("drone") else None,
                    "assigned_at": a.get("assigned_at")
                }
                for a in all_assignments[-5:]
            ],
            "assignment_history_count": len(
                self.assignment_manager.get_history()
            )
        }
    
    def get_detailed_report(self) -> Dict:
        """Get comprehensive system report"""
        return {
            "system_status": self.get_system_status(),
            "assignments": self.assignment_manager.get_assignment_report(),
            "unassigned_missions": [
                self.analyze_mission_conflicts(m) for m in self.missions
                if m.is_unassigned()
            ]
        }
    
    # ===== CONVERSATIONAL INTERFACE =====
    
    def process_request(self, request: str) -> Dict:
        """
        Process natural language request
        
        Supported request types:
        - "assign <mission>" → Assign unspecified mission
        - "status" → Get system status
        - "conflicts" → List all conflicts
        - "assignments" → List current assignments
        - "unassigned" → List unassigned missions
        - "pilot <name>" → Get pilot info
        - "drone <id>" → Get drone info
        - "mission <id>" → Get mission info
        
        Returns:
            Response dict
        """
        request_lower = request.lower().strip()
        
        # Status request
        if "status" in request_lower:
            return {
                "type": "system_status",
                "data": self.get_system_status()
            }
        
        # Assign request
        if "assign" in request_lower:
            unassigned = [m for m in self.missions if m.is_unassigned()]
            if not unassigned:
                return {
                    "type": "message",
                    "message": "All missions are already assigned"
                }
            
            results = []
            for mission in unassigned:
                result = self.process_mission_assignment(mission)
                results.append(result)
            
            return {
                "type": "assignments",
                "results": results
            }
        
        # Conflicts request
        if "conflict" in request_lower:
            unassigned = [m for m in self.missions if m.is_unassigned()]
            return {
                "type": "conflicts",
                "conflicts": [
                    self.analyze_mission_conflicts(m) for m in unassigned
                ]
            }
        
        # Assignments request
        if "assignment" in request_lower:
            return {
                "type": "assignments",
                "data": self.assignment_manager.get_assignment_report()
            }
        
        # Unassigned request
        if "unassigned" in request_lower:
            unassigned = [m for m in self.missions if m.is_unassigned()]
            return {
                "type": "missions",
                "missions": [
                    self.get_mission_status(m) for m in unassigned
                ]
            }
        
        # Pilot request
        if request_lower.startswith("pilot"):
            pilot_name = request_lower.replace("pilot", "").strip()
            matching = [p for p in self.pilots 
                       if pilot_name in p.name.lower() or p.name.lower() in pilot_name]
            if matching:
                return {
                    "type": "pilot",
                    "data": [self.get_pilot_availability(p) for p in matching]
                }
        
        # Drone request
        if request_lower.startswith("drone"):
            drone_id = request_lower.replace("drone", "").strip()
            matching = [d for d in self.drones 
                       if drone_id in d.id.lower() or d.id.lower() in drone_id]
            if matching:
                return {
                    "type": "drone",
                    "data": [self.get_drone_availability(d) for d in matching]
                }
        
        # Mission request
        if request_lower.startswith("mission"):
            mission_id = request_lower.replace("mission", "").strip()
            matching = [m for m in self.missions 
                       if mission_id in m.project_id.lower() or m.project_id.lower() in mission_id]
            if matching:
                return {
                    "type": "mission",
                    "data": [self.get_mission_status(m) for m in matching]
                }
        
        # Default
        return {
            "type": "help",
            "message": "Supported commands: status, assign, conflicts, assignments, unassigned, pilot <name>, drone <id>, mission <id>"
        }
    
    def handle_urgent_reassignment(self, mission_id: str) -> Dict:
        """
        Handle urgent reassignment for a specific high-priority mission
        
        Checks if mission is high priority and has conflicts,
        then automatically finds and assigns next best candidate
        """
        self.refresh_data()  # Get latest data
        
        result = self.urgent_reassignment_service.handle_urgent_mission(
            mission_id=mission_id,
            pilots=self.pilots,
            drones=self.drones,
            missions=self.missions
        )
        
        # Update local data after reassignment
        self.refresh_data()
        
        return result
    
    def handle_all_urgent_reassignments(self) -> Dict:
        """
        Check and reassign all high-priority missions with conflicts
        
        Returns comprehensive summary of all reassignments
        """
        self.refresh_data()  # Get latest data
        
        result = self.urgent_reassignment_service.handle_all_high_priority_missions(
            pilots=self.pilots,
            drones=self.drones,
            missions=self.missions
        )
        
        # Update local data after reassignments
        self.refresh_data()
        
        return result
    
    def get_reassignment_log(self) -> List[Dict]:
        """Get complete reassignment event log"""
        return self.urgent_reassignment_service.get_reassignment_log()
