# API

## Error Format
All write operations return a structured error on failure:

```
{
  "status": "FAILED",
  "reason": "Specific failure reason"
}
```

## Read Endpoints
- GET /api/pilots
- GET /api/drones
- GET /api/missions
- GET /api/system/status
- GET /api/system/report
- GET /api/assignments
- GET /api/assignments/history
- GET /api/conflicts
- GET /api/conflicts/{mission_id}
- GET /api/pilots/{pilot_name}
- GET /api/drones/{drone_id}
- GET /api/missions/{mission_id}
- GET /api/reassignment_log

## Write Endpoints
- POST /api/update_pilot_status
  - Body: {"pilot_name": "Arjun", "new_status": "Unavailable"}
- POST /api/assign_mission
  - Body: {"mission_id": "PRJ001", "pilot_name": "Arjun", "drone_id": "D001"}
- POST /api/assignments/process
- POST /api/assignments/recommend
- POST /api/urgent_reassign/{mission_id}
- POST /api/urgent_reassign_all

## Notes
- Urgent reassignment triggers on priority in ["high", "urgent"].
- Mission assignment auto-creates columns: status, assigned_pilot, assigned_drone.