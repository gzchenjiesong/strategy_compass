---
title: Conflict Resolution SOP
type: sop
created: 2026-05-13
tags: [agent-ops, collaboration, governance]
---

# Conflict Resolution Between Agents/Roles

## Purpose
Define how to detect, escalate, and resolve conflicts when multiple agents or roles attempt to modify the same document or disagree on implementation approaches.

## Scope
- Document edit collisions (two agents editing the same file)
- Architectural disagreements (schema, API design, tech stack)
- Priority conflicts (urgent fix vs. planned refactor)
- Data source disputes (which source of truth to use)

## Detection

| Signal | Detection Method |
|--------|------------------|
| Git merge conflict | `git status` shows unmerged paths |
| Concurrent file lock | File modified timestamp newer than read time |
| Schema mismatch | Validation errors after another agent's update |
| Circular dependency | Import errors or infinite loops in agent calls |

## Resolution Protocol

### Step 1: Pause & Notify (T+0)
- Stop all writes to the contested resource
- Post a brief conflict notice in the shared log
- Tag the other agent/role involved

### Step 2: Assess Impact (T+5min)
- Determine if the conflict is:
  - **Cosmetic** (formatting, comments) → merge manually
  - **Structural** (schema, API) → schedule a sync meeting
  - **Data** (source values) → escalate to data owner

### Step 3: Decide Authority
| Conflict Type | Decision Owner |
|---------------|----------------|
| Frontend vs Backend API shape | Backend owner (consumer-driven contract) |
| Database schema | Data architect / senior engineer |
| Business logic | Product owner or domain expert |
| DevOps / deployment | SRE / infrastructure lead |

### Step 4: Merge or Rollback
- If one change is clearly newer/better: keep it, document the discard
- If both have value: create a merge branch, integrate both, test
- If deadlock persists: escalate to human within 30 minutes

## Prevention Checklist
- [ ] Use atomic file locks for critical documents
- [ ] Maintain a shared `CHANGELOG.md` for schema-level changes
- [ ] Assign clear ownership per module (see `MODULE_OWNERS.md`)
- [ ] Run pre-commit validation scripts before any write
- [ ] Use feature branches for non-trivial changes

## Escalation Path
1. Agent-to-agent direct discussion (5 min)
2. Involve module owner (15 min)
3. Human review required (30 min)
4. Emergency override (human decides, agents comply)

## Post-Resolution
- Document the conflict and resolution in `memory/YYYY-MM-DD.md`
- Update this SOP if a new pattern emerges
- Schedule a retro if conflicts exceed 2 per week
