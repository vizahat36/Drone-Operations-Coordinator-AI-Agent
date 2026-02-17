# Decision Log

## Assumptions
- Google Sheets headers are present but may be lowercase or contain extra whitespace.
- Skills and certifications are comma-separated in sheet cells.
- Missions can be reassigned only when priority is High or Urgent.

## Trade-offs
- Column discovery is case-insensitive and trimmed to reduce configuration errors.
- Mission assignment auto-creates status/assigned_pilot/assigned_drone columns to keep workflows consistent.
- Write endpoints return structured failure reasons (status FAILED) to avoid silent errors.

## Urgent Reassignment Interpretation
- Trigger condition: mission.priority in {"high", "urgent"}.
- Reassignment happens only when ConflictEngine detects invalid current assignment.
- DecisionEngine selects next best available pilot/drone based on constraints and scoring.
- AssignmentManager records reassignment history; SheetsService persists updates.