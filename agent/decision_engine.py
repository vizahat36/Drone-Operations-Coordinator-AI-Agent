"""
Decision Engine for pilot and drone matching
Implements constraint satisfaction and ranking logic
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.pilot import Pilot
from models.drone import Drone
from models.mission import Mission
from utils.cost_utils import calculate_pilot_cost, is_within_budget
from utils.data_parser import dates_overlap


class DecisionEngine:
    """
    Decision engine for matching pilots and drones to missions
    Uses constraint satisfaction with cost optimization
    """
    
    def __init__(self):
        """Initialize decision engine"""
        self.match_log = []
    
    # ===== PILOT MATCHING =====
    
    def match_pilots(self, mission: Mission, pilots: List[Pilot], assigned_pilots: Optional[Dict] = None) -> List[Dict]:
        """
        Find valid pilots for a mission.
        
        Constraints (in order):
        1. Availability
        2. Skills match
        3. Certifications match
        4. No schedule overlap
        5. Cost within budget
        
        Returns:
            List of dicts: [{"pilot": Pilot, "cost": float, "score": float}, ...]
            Sorted by cost (cheapest first)
        """
        valid_candidates = []
        assigned_pilots = assigned_pilots or {}
        
        for pilot in pilots:
            reasons = []  # Track why a pilot was rejected
            
            # 1️⃣ Check availability
            if not pilot.is_available():
                reasons.append(f"Status: {pilot.status}")
                continue
            
            # 2️⃣ Check skills
            if not pilot.has_all_skills(mission.required_skills):
                missing_skills = [s for s in mission.required_skills if s not in pilot.skills]
                reasons.append(f"Missing skills: {missing_skills}")
                continue
            
            # 3️⃣ Check certifications
            if not pilot.has_all_certifications(mission.required_certs):
                missing_certs = [c for c in mission.required_certifications if c not in pilot.certifications]
                reasons.append(f"Missing certs: {missing_certs}")
                continue
            
            # 4️⃣ Check for schedule overlap with other assigned missions
            if pilot.name in assigned_pilots:
                other_mission = assigned_pilots[pilot.name]
                if dates_overlap(mission.start_date, mission.end_date, 
                               other_mission.start_date, other_mission.end_date):
                    reasons.append(f"Schedule conflict with {other_mission.name}")
                    continue
            
            # 5️⃣ Calculate cost
            cost = calculate_pilot_cost(
                pilot.daily_rate,
                (mission.end_date - mission.start_date).days + 1
            )
            
            # 6️⃣ Check budget
            if not is_within_budget(mission.budget, cost):
                reasons.append(f"Cost ₹{cost} exceeds budget ₹{mission.budget}")
                continue
            
            # 7️⃣ Calculate match score
            score = self._calculate_pilot_score(pilot, mission, cost)
            
            valid_candidates.append({
                "pilot": pilot,
                "cost": cost,
                "score": score,
                "match_percentage": score
            })
        
        # Sort by cost (cheapest first)
        valid_candidates.sort(key=lambda x: x["cost"])
        
        return valid_candidates
    
    def _calculate_pilot_score(self, pilot: Pilot, mission: Mission, cost: float) -> float:
        """
        Calculate match score for pilot (0-100).
        Factors:
        - Skill match (40%)
        - Certification match (30%)
        - Cost efficiency (20%)
        - Location match (10%)
        """
        score = 0.0
        
        # Skill match: 40 points
        matching_skills = sum(1 for skill in mission.required_skills if skill in pilot.skills)
        if mission.required_skills:
            skill_score = (matching_skills / len(mission.required_skills)) * 40
        else:
            skill_score = 40
        score += skill_score
        
        # Certification match: 30 points
        matching_certs = sum(1 for cert in mission.required_certifications if cert in pilot.certifications)
        if mission.required_certifications:
            cert_score = (matching_certs / len(mission.required_certifications)) * 30
        else:
            cert_score = 30
        score += cert_score
        
        # Cost efficiency: 20 points (lower cost = higher score)
        # Assume 10000 as average daily rate * 5 days = 50000 budget
        cost_ratio = min(cost / max(mission.budget, 1), 1.0)
        cost_score = (1 - cost_ratio) * 20
        score += cost_score
        
        # Location match: 10 points
        location_score = 10 if pilot.location == mission.location else 5
        score += location_score
        
        return round(score, 2)
    
    # ===== DRONE MATCHING =====
    
    def match_drones(self, mission: Mission, drones: List[Drone], assigned_drones: Optional[Dict] = None) -> List[Dict]:
        """
        Find valid drones for a mission.
        
        Constraints:
        1. Availability
        2. Capability match
        3. Weather compatibility
        4. No schedule overlap
        5. Maintenance not during mission
        
        Returns:
            List of dicts: [{"drone": Drone, "score": float}, ...]
            Sorted by score (best first)
        """
        valid_candidates = []
        assigned_drones = assigned_drones or {}
        
        for drone in drones:
            reasons = []
            
            # 1️⃣ Check availability
            if not drone.is_available():
                reasons.append(f"Status: {drone.status}")
                continue
            
            # 2️⃣ Check capability (simplified - exact match)
            # In real system, might check if drone has required capability
            # For now, just ensure it's not limited
            
            # 3️⃣ Check weather compatibility (simplified)
            # Weather ratings: IP20 < IP45 < IP54 < IP67 < Waterproof
            # Rainy weather needs IP44+, Heavy Rain needs IP54+, Waterproof
            weather_compatible = self._check_weather_compatibility(drone, mission)
            if not weather_compatible:
                reasons.append("Weather incompatible")
                continue
            
            # 4️⃣ Check for schedule overlap
            if drone.id in assigned_drones:
                other_mission = assigned_drones[drone.id]
                if dates_overlap(mission.start_date, mission.end_date,
                               other_mission.start_date, other_mission.end_date):
                    reasons.append(f"Schedule conflict with {other_mission.name}")
                    continue
            
            # 5️⃣ Check maintenance schedule
            if drone.maintenance_hours > 0:
                # If maintenance is needed, check if it can be done before mission
                # This is simplified - in real system, track actual maintenance dates
                maintenance_ok = True
                if not maintenance_ok:
                    reasons.append(f"Maintenance required ({drone.maintenance_hours}h)")
                    continue
            
            # Calculate match score
            score = self._calculate_drone_score(drone, mission)
            
            valid_candidates.append({
                "drone": drone,
                "score": score,
                "match_percentage": score
            })
        
        # Sort by score (best first)
        valid_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return valid_candidates
    
    def _check_weather_compatibility(self, drone: Drone, mission: Mission) -> bool:
        """
        Check if drone weather rating is compatible with mission.
        (Simplified - in real system, would check actual weather forecast)
        
        Weather ratings:
        - IP20: Light conditions
        - IP45: Light rain
        - IP54: Moderate rain
        - IP67: Heavy rain
        - Waterproof: Extreme conditions
        """
        # For now, accept all drones (in real system, check mission weather field)
        return True
    
    def _calculate_drone_score(self, drone: Drone, mission: Mission) -> float:
        """
        Calculate drone match score (0-100).
        Factors:
        - Capability match (50%)
        - Weather rating (30%)
        - Location match (20%)
        """
        score = 0.0
        
        # Capability: 50 points
        capability_score = 50  # All available drones assumed capable
        score += capability_score
        
        # Weather rating: 30 points
        weather_ratings = {"IP20": 10, "IP45": 20, "IP54": 25, "IP67": 30, "Waterproof": 30}
        weather_score = weather_ratings.get(drone.weather_rating, 15)
        score += weather_score
        
        # Location: 20 points
        location_score = 20 if drone.location == mission.location else 10
        score += location_score
        
        return round(score, 2)
    
    # ===== COMBINED MATCHING =====
    
    def find_best_assignment(
        self, 
        mission: Mission, 
        pilots: List[Pilot], 
        drones: List[Drone],
        assigned_pilots: Optional[Dict] = None,
        assigned_drones: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Find best pilot-drone combination for a mission.
        
        Returns:
            Dict with pilot, drone, total_cost if found, None otherwise
        """
        assigned_pilots = assigned_pilots or {}
        assigned_drones = assigned_drones or {}
        
        # Get valid pilots and drones
        valid_pilots = self.match_pilots(mission, pilots, assigned_pilots)
        valid_drones = self.match_drones(mission, drones, assigned_drones)
        
        if not valid_pilots or not valid_drones:
            return None
        
        # Pick cheapest pilot and best drone
        best_pilot = valid_pilots[0]
        best_drone = valid_drones[0]
        
        return {
            "pilot": best_pilot["pilot"],
            "drone": best_drone["drone"],
            "pilot_cost": best_pilot["cost"],
            "pilot_score": best_pilot["score"],
            "drone_score": best_drone["score"],
            "total_score": (best_pilot["score"] + best_drone["score"]) / 2
        }
    
    def rank_assignments(
        self,
        mission: Mission,
        pilots: List[Pilot],
        drones: List[Drone],
        assigned_pilots: Optional[Dict] = None,
        assigned_drones: Optional[Dict] = None,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Rank all valid pilot-drone combinations for a mission.
        
        Returns:
            List of top valid assignments (sorted by combined score)
        """
        assigned_pilots = assigned_pilots or {}
        assigned_drones = assigned_drones or {}
        
        valid_pilots = self.match_pilots(mission, pilots, assigned_pilots)
        valid_drones = self.match_drones(mission, drones, assigned_drones)
        
        assignments = []
        
        for pilot_match in valid_pilots:
            for drone_match in valid_drones:
                combined_score = (pilot_match["score"] + drone_match["score"]) / 2
                
                assignments.append({
                    "pilot": pilot_match["pilot"],
                    "drone": drone_match["drone"],
                    "pilot_cost": pilot_match["cost"],
                    "pilot_score": pilot_match["score"],
                    "drone_score": drone_match["score"],
                    "combined_score": combined_score
                })
        
        # Sort by combined score
        assignments.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return assignments[:top_n]
    
    # ===== CONFLICT DETECTION (used in matching) =====
    
    def get_conflicts(
        self,
        mission: Mission,
        pilots: List[Pilot],
        drones: List[Drone]
    ) -> Dict:
        """
        Get all conflicts preventing pilot/drone assignment.
        
        Returns:
            Dict with pilot_conflicts and drone_conflicts
        """
        pilot_conflicts = []
        drone_conflicts = []
        
        # Check each pilot
        for pilot in pilots:
            if not pilot.is_available():
                pilot_conflicts.append({
                    "pilot": pilot.name,
                    "reason": f"Status is {pilot.status}",
                    "type": "availability"
                })
            elif not pilot.has_all_skills(mission.required_skills):
                missing = [s for s in mission.required_skills if s not in pilot.skills]
                pilot_conflicts.append({
                    "pilot": pilot.name,
                    "reason": f"Missing skills: {missing}",
                    "type": "skills"
                })
            elif not pilot.has_all_certifications(mission.required_certifications):
                missing = [c for c in mission.required_certifications if c not in pilot.certifications]
                pilot_conflicts.append({
                    "pilot": pilot.name,
                    "reason": f"Missing certs: {missing}",
                    "type": "certifications"
                })
        
        # Check each drone
        for drone in drones:
            if not drone.is_available():
                drone_conflicts.append({
                    "drone": drone.id,
                    "reason": f"Status is {drone.status}",
                    "type": "availability"
                })
        
        return {
            "mission_id": mission.id,
            "mission_name": mission.name,
            "pilot_conflicts": pilot_conflicts,
            "drone_conflicts": drone_conflicts,
            "viable_pilots": len(pilots) - len(pilot_conflicts),
            "viable_drones": len(drones) - len(drone_conflicts)
        }
