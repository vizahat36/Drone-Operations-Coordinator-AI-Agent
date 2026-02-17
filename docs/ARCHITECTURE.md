# Architecture

## System Overview
The system coordinates pilots, drones, and missions using a layered service design. Data is stored in Google Sheets and accessed through a dedicated service layer. Assignment logic uses constraint checks and scoring, with urgent reassignment handling high-priority disruptions.

## Core Components
- SheetsService: Reads and writes Google Sheets data and performs column normalization.
- ConflictEngine: Detects constraint violations across pilots, drones, and missions.
- DecisionEngine: Ranks and selects candidates based on skills, certifications, cost, and availability.
- AssignmentManager: Tracks assignments, prevents double-booking, and manages reassignment.
- UrgentReassignmentService: Monitors high/urgent missions and auto-reassigns on conflicts.

## Data Flow
1. SheetsService loads pilots, drones, and missions.
2. DecisionEngine evaluates eligible pilots/drones.
3. ConflictEngine validates constraints and reports issues.
4. AssignmentManager records assignments and history.
5. UrgentReassignmentService re-evaluates high/urgent missions and triggers reassignment.
6. SheetsService persists updates back to Google Sheets.

## Failure Handling
- Write endpoints return structured failure reasons.
- Column mapping is dynamic and case-insensitive.
- Missing mission assignment columns are auto-created when assigning.