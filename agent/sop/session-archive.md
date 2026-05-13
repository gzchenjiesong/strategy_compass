# Session Archiving (SOP)

> When and how to archive a development session, ensuring clean handoffs.

## When to Archive

Archive a session when any of the following occur:

- [ ] A feature branch is merged or closed
- [ ] A multi-day task is paused for > 24 hours
- [ ] The active context shifts to a new module or major bug
- [ ] A sub-agent session ends and its output needs preservation
- [ ] End of a sprint / milestone

## What to Update Before Archiving

1. **Progress tracker**
   - Update `agent/memory-bank/progress.md` with completed / in-progress / blocked items
   - Mark finished tasks with ✅ and link the commit or PR

2. **Active context**
   - Update `agent/memory-bank/active-context.md`:
     - Current phase
     - Next immediate action
     - Known blockers
     - Open questions

3. **Daily log**
   - Append a summary to `agent/memory/YYYY-MM-DD.md`
   - Include: what was done, decisions made, issues hit, next steps

4. **Design sync**
   - If code changed, run `./scripts/check-design-sync.sh` (or manual review)
   - Update design docs if they drifted from implementation

## Handoff Template

Copy this into `agent/memory/YYYY-MM-DD.md` (or a dedicated handoff note):

```markdown
## Session Handoff — YYYY-MM-DD

### Completed
- Item 1 (commit: `abc1234`)
- Item 2

### In Progress
- Item 3 (blocked on: …)

### Next Action
- [ ] Next concrete step for the next session

### Open Questions
- Question 1

### Files Touched
- `backend/app/...`
- `frontend/src/...`

### Notes
- Anything the next session should know
```

## Archive Location

Move obsolete / superseded files to `agent/archive/` with a dated prefix:

```
agent/archive/2026-05-13-startup-prompt-skill.md
```

Keep the archive flat; use filename dates for sorting.
