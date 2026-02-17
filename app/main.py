"""
Main application entry point
Skylark Drone Operations Coordinator Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.sheets_service import SheetsService
from agent.controller import Controller

# Initialize FastAPI app
app = FastAPI(
    title="Skylark Agent",
    description="Drone Operations Coordinator AI Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
sheets_service = SheetsService()
controller = Controller()

# Request Models
class AssignmentRequest(BaseModel):
    mission_id: str
    pilot_name: str
    drone_id: str

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {"message": "Skylark Agent Running"}

@app.get("/api/pilots")
async def get_pilots():
    """Get all pilots from Google Sheets"""
    pilots = sheets_service.read_pilots()
    return {
        "count": len(pilots),
        "pilots": [
            {
                "pilot_id": p.pilot_id,
                "name": p.name,
                "location": p.location,
                "skills": p.skills,
                "certifications": p.certifications,
                "status": p.status,
                "current_assignment": p.current_assignment,
                "available_from": p.available_from,
                "daily_rate_inr": p.daily_rate_inr
            }
            for p in pilots
        ]
    }

@app.get("/api/drones")
async def get_drones():
    """Get all drones from Google Sheets"""
    drones = sheets_service.read_drones()
    return {
        "count": len(drones),
        "drones": [
            {
                "drone_id": d.drone_id,
                "model": d.model,
                "location": d.location,
                "status": d.status,
                "capabilities": d.capabilities,
                "weather_resistance": d.weather_resistance,
                "maintenance_due": d.maintenance_due,
                "current_assignment": d.current_assignment
            }
            for d in drones
        ]
    }

@app.get("/api/missions")
async def get_missions():
    """Get all missions from Google Sheets"""
    missions = sheets_service.read_missions()
    return {
        "count": len(missions),
        "missions": [
            {
                "project_id": m.project_id,
                "client": m.client,
                "location": m.location,
                "start_date": str(m.start_date),
                "end_date": str(m.end_date),
                "required_skills": m.required_skills,
                "required_certs": m.required_certs,
                "mission_budget_inr": m.mission_budget_inr,
                "priority": m.priority,
                "status": m.status,
                "assigned_pilot": m.assigned_pilot,
                "assigned_drone": m.assigned_drone,
                "weather_forecast": m.weather_forecast
            }
            for m in missions
        ]
    }
# ===== SYSTEM STATUS ENDPOINTS =====

@app.get("/api/system/status")
async def get_system_status():
    """Get overall system status"""
    return controller.get_system_status()

@app.get("/api/system/report")
async def get_system_report():
    """Get comprehensive system report"""
    return controller.get_detailed_report()

# ===== ASSIGNMENT ENDPOINTS =====

@app.post("/api/assignments/process")
async def process_assignments():
    """Process all unassigned missions"""
    results = controller.process_multiple_missions()
    return {
        "total": len(results),
        "results": results
    }

@app.post("/api/assignments/recommend")
async def recommend_assignments():
    """Get assignment recommendations for unassigned missions"""
    recommendations = []
    for mission in controller.missions:
        if mission.is_unassigned():
            rec = controller.get_assignment_recommendations(mission)
            recommendations.append(rec)
    return {
        "total": len(recommendations),
        "recommendations": recommendations
    }

@app.get("/api/assignments")
async def get_assignments():
    """Get current assignments"""
    return controller.assignment_manager.get_assignment_report()

@app.get("/api/assignments/history")
async def get_assignment_history():
    """Get assignment history"""
    return {
        "count": len(controller.assignment_manager.get_history()),
        "history": controller.assignment_manager.get_history()
    }

# ===== CONFLICT DETECTION ENDPOINTS =====

@app.get("/api/conflicts")
async def get_conflicts():
    """Get conflicts for all unassigned missions"""
    conflicts = []
    for mission in controller.missions:
        if mission.is_unassigned():
            conflict_report = controller.analyze_mission_conflicts(mission)
            conflicts.append(conflict_report)
    return {
        "total": len(conflicts),
        "conflicts": conflicts
    }

@app.get("/api/conflicts/{mission_id}")
async def get_mission_conflicts(mission_id: str):
    """Get detailed conflicts for a specific mission"""
    mission = next((m for m in controller.missions if m.project_id == mission_id), None)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return controller.analyze_mission_conflicts(mission)

# ===== PILOT/DRONE/MISSION QUERY ENDPOINTS =====

@app.get("/api/pilots/{pilot_name}")
async def get_pilot_info(pilot_name: str):
    """Get specific pilot info"""
    pilot = next((p for p in controller.pilots 
                 if pilot_name.lower() in p.name.lower()), None)
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot not found")
    
    return controller.get_pilot_availability(pilot)

@app.get("/api/drones/{drone_id}")
async def get_drone_info(drone_id: str):
    """Get specific drone info"""
    drone = next((d for d in controller.drones 
                 if drone_id.lower() in d.drone_id.lower()), None)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    return controller.get_drone_availability(drone)

@app.get("/api/missions/{mission_id}")
async def get_mission_info(mission_id: str):
    """Get specific mission info"""
    mission = next((m for m in controller.missions if m.project_id == mission_id), None)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return controller.get_mission_status(mission)

# ===== WRITE ENDPOINTS =====

class UpdatePilotStatusRequest(BaseModel):
    pilot_name: str
    new_status: str

@app.post("/api/update_pilot_status")
async def update_pilot_status(request: UpdatePilotStatusRequest):
    """
    Update pilot status in Google Sheets
    
    Example: {"pilot_name": "Alice Chen", "new_status": "Unavailable"}
    """
    success, reason = sheets_service.update_pilot_status_detail(
        request.pilot_name,
        request.new_status
    )
    
    if success:
        return {
            "status": "SUCCESS",
            "message": f"Updated {request.pilot_name} status to {request.new_status}"
        }
    
    return JSONResponse(
        status_code=400,
        content={
            "status": "FAILED",
            "reason": reason
        }
    )

@app.post("/api/assign_mission")
async def assign_mission_endpoint(request: AssignmentRequest):
    """
    Full assignment lifecycle - updates pilot, drone, and mission in Google Sheets
    
    Steps:
    1. Update pilot status to "Unavailable"
    2. Update drone status to "Deployed"
    3. Update mission with assigned pilot/drone and status to "Assigned"
    
    Example: {
        "mission_id": "M001",
        "pilot_name": "Vizahat",
        "drone_id": "D001"
    }
    """
    # Step 1: Update pilot status
    pilot_updated, pilot_reason = sheets_service.update_pilot_status_detail(
        request.pilot_name,
        "Unavailable"
    )
    if not pilot_updated:
        return JSONResponse(
            status_code=400,
            content={
                "status": "FAILED",
                "reason": pilot_reason
            }
        )
    
    # Step 2: Update drone status
    drone_updated, drone_reason = sheets_service.update_drone_status_detail(
        request.drone_id,
        "Deployed"
    )
    if not drone_updated:
        return JSONResponse(
            status_code=400,
            content={
                "status": "FAILED",
                "reason": drone_reason
            }
        )
    
    # Step 3: Assign mission
    mission_updated, mission_reason = sheets_service.assign_mission_detail(
        request.mission_id,
        request.pilot_name,
        request.drone_id
    )
    if not mission_updated:
        return JSONResponse(
            status_code=400,
            content={
                "status": "FAILED",
                "reason": mission_reason
            }
        )
    
    return {
        "status": "SUCCESS",
        "message": f"Successfully assigned mission {request.mission_id}",
        "details": {
            "mission_id": request.mission_id,
            "pilot": request.pilot_name,
            "pilot_status": "Unavailable",
            "drone": request.drone_id,
            "drone_status": "Deployed",
            "mission_status": "Assigned"
        }
    }

# ===== URGENT REASSIGNMENT ENDPOINTS =====

@app.post("/api/urgent_reassign/{mission_id}")
async def handle_urgent_reassignment(mission_id: str):
    """
    Trigger urgent reassignment for a specific high-priority mission
    
    This endpoint:
    1. Checks if mission is high priority
    2. Detects conflicts in current assignment
    3. Automatically finds next best candidate
    4. Updates Google Sheets
    5. Returns reassignment summary
    
    Example: POST /api/urgent_reassign/M001
    """
    result = controller.handle_urgent_reassignment(mission_id)
    return result

@app.post("/api/urgent_reassign_all")
async def handle_all_urgent_reassignments():
    """
    Trigger urgent reassignment check for ALL high-priority missions
    
    Automatically:
    1. Finds all high-priority missions
    2. Checks validity of current assignments
    3. Detects any conflicts
    4. Reassigns resources if needed
    5. Returns comprehensive summary
    
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
    result = controller.handle_all_urgent_reassignments()
    return result

@app.get("/api/reassignment_log")
async def get_reassignment_log():
    """
    Get complete event log of all reassignment operations
    
    Returns all reassignment events with timestamps and details
    """
    log = controller.get_reassignment_log()
    return {
        "total_events": len(log),
        "events": log
    }

# ===== CONVERSATIONAL INTERFACE =====

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Conversational API - Process natural language requests
    
    Supported commands:
    - "status" → Get system status
    - "assign" → Auto-assign all unassigned missions
    - "conflicts" → Show all conflicts
    - "assignments" → Get current assignments
    - "unassigned" → List unassigned missions
    - "pilot <name>" → Get pilot info
    - "drone <id>" → Get drone info
    - "mission <id>" → Get mission info
    """
    response = controller.process_request(request.message)
    return response