# Decision Log

## 1. Key Assumptions

- Google Sheets is the authoritative data source.
- Sheet headers may vary in case or contain whitespace; column mapping must be dynamic.
- Skills and certifications are stored as comma-separated strings.
- Missions are eligible for urgent reassignment only if priority is High or Urgent.
- A mission without assignment columns must still be assignable (columns auto-created if missing).

## 2. Architectural Decisions

### Domain-Driven Structure

The system is divided into:

- **SheetsService** → Data persistence layer
- **ConflictEngine** → Constraint validation
- **DecisionEngine** → Scoring & optimal selection
- **AssignmentManager** → State tracking & history
- **Controller** → Orchestration layer

This separation ensures:
- Clear responsibilities
- Testable components
- No tight coupling between decision logic and persistence

### Google Sheets as Database

**Trade-off:**

Pros:
- Easy demonstration
- Real-time sync
- No infra setup

Cons:
- No transactions
- Limited concurrency

**Mitigation:**
- Atomic write sequencing
- Structured failure responses
- Auto column creation to prevent schema drift

## 3. Matching & Scoring Strategy

The DecisionEngine uses multi-constraint filtering:

- Availability
- Skill match
- Certification match
- Weather compatibility
- Budget compliance
- Schedule overlap

Candidates are ranked using weighted scoring:
- Skill match
- Certification match
- Cost efficiency
- Location alignment

This enables deterministic, explainable selection.

## 4. Conflict Handling Strategy

ConflictEngine detects:

- Double booking (date overlap)
- Skill mismatch
- Certification mismatch
- Budget overrun
- Maintenance conflicts
- Weather incompatibility
- Location mismatch

Assignments proceed only when all constraints pass.

Failures return structured JSON responses with explicit reasons.

## 5. Urgent Reassignment Interpretation

**Trigger:**
- mission.priority ∈ {"High", "Urgent"}

**Process:**
1. Validate current assignment.
2. If conflict detected → find alternatives.
3. Re-score candidates.
4. Select highest scoring valid pair.
5. Persist updates to Sheets.
6. Log reassignment event.

This ensures operational continuity without human intervention.

## 6. Trade-offs & Future Improvements

### Trade-offs

- No transactional rollback (Google Sheets limitation)
- In-memory assignment tracking (sufficient for prototype scale)
- Rule-based NLP instead of full LLM intent parsing

### With More Time

- Add transactional safety via shadow state validation
- Introduce caching layer
- Add audit sheet for persistent event logging
- Replace rule-based chat with LLM-powered orchestration
- Add concurrency locks for multi-user scenarios