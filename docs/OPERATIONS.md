# Operations

## Deployment (Minimal)
1. Install dependencies:
   - `pip install -r requirements.txt`
2. Start API:
   - `python -m uvicorn app.main:app --reload`

## Environment Variables
- GOOGLE_CREDENTIALS_PATH: Path to service account JSON.
- SHEET_NAME: Spreadsheet name (default: Skylark).
- SHEET_ID: Optional explicit sheet ID.
- USE_MOCK_DATA: True/False for real sheets vs mock.

## Google Sheets Schema
Pilots:
- pilot_id, name, skills, certifications, location, status, current_assignment, available_from, daily_rate_inr

Drones:
- drone_id, model, capabilities, status, location, current_assignment, maintenance_due, weather_resistance

Missions:
- project_id, client, location, required_skills, required_certs, start_date, end_date, priority, mission_budget_inr, weather_forecast
- auto-added on assignment: status, assigned_pilot, assigned_drone

## Data Conventions
- Headers are case-insensitive and trimmed.
- Skills and certifications are comma-separated in sheets.
- Dates are parsed if present; empty values are allowed.