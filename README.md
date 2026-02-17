# Skylark Drones - AI Operations Coordinator

## Overview
Skylark coordinates pilots, drones, and missions using Google Sheets as the data source.
It detects conflicts, ranks candidates, and assigns resources based on skills, certifications,
availability, and budget. High and urgent missions receive autonomous reassignment if conflicts
arise. The system exposes a FastAPI interface for reads, assignments, conflict analysis, and
urgent reassignment.

## Architecture
- SheetsService: data access and column normalization for Google Sheets.
- ConflictEngine: constraint validation for pilots, drones, and missions.
- DecisionEngine: candidate scoring and ranking.
- AssignmentManager: assignment tracking and history.
- UrgentReassignmentService: automated reassignment for high/urgent missions.

## Key Features
- Dynamic column mapping with explicit error reasons.
- Constraint-based matching and conflict reporting.
- Autonomous urgent reassignment for high/urgent missions.
- Clean API responses with structured failure reasons.

## API Endpoints
- Reads: /api/pilots, /api/drones, /api/missions, /api/system/status
- Writes: /api/assign_mission, /api/update_pilot_status
- Urgent: /api/urgent_reassign/{mission_id}, /api/urgent_reassign_all

## Deployment Instructions
- Install: `pip install -r requirements.txt`
- Run: `python -m uvicorn app.main:app --reload`

## Documentation
See [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md).
