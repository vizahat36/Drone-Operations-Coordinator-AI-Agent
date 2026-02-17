"""
Main application entry point
Skylark Drone Operations Coordinator Agent
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.sheets_service import SheetsService

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

# Initialize Sheets Service
sheets_service = SheetsService()

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
                "name": p.name,
                "location": p.location,
                "skills": p.skills,
                "certifications": p.certifications,
                "status": p.status,
                "daily_rate": p.daily_rate
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
                "id": d.id,
                "name": d.name,
                "location": d.location,
                "status": d.status,
                "capability": d.capability,
                "weather_rating": d.weather_rating,
                "maintenance_hours": d.maintenance_hours
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
                "id": m.id,
                "name": m.name,
                "location": m.location,
                "start_date": str(m.start_date),
                "end_date": str(m.end_date),
                "required_skills": m.required_skills,
                "required_certifications": m.required_certifications,
                "budget": m.budget,
                "priority": m.priority,
                "status": m.status,
                "assigned_pilot": m.assigned_pilot,
                "assigned_drone": m.assigned_drone
            }
            for m in missions
        ]
    }
