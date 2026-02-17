# Phase 7 Demo Scenario

## Goal
Show full assignment lifecycle and urgent reassignment with clear API behavior.

## Steps
1. Assign PRJ001 to Arjun/D001:
   - POST /api/assign_mission
   - Body: {"mission_id":"PRJ001","pilot_name":"Arjun","drone_id":"D001"}

2. Manually change Arjun status to "On Leave" in Google Sheets.

3. Trigger urgent reassignment:
   - POST /api/urgent_reassign/PRJ001

4. Verify:
   - Missions sheet updated with assigned_pilot/assigned_drone/status.
   - Pilots/Drones current_assignment updated.

5. Retrieve reassignment log:
   - GET /api/reassignment_log

## Expected Results
- /api/assign_mission returns status SUCCESS.
- /api/urgent_reassign/PRJ001 returns REASSIGNED or FAILED with reason.
- Reassignment log contains a timestamped entry.