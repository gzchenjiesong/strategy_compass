---
title: Database Schema Migration SOP
type: sop
created: 2026-05-13
tags: [database, migration, data-integrity]
---

# Database Schema Change Procedures

## Purpose
Ensure all schema changes are safe, reversible, and do not break existing agents or downstream consumers.

## Principles
1. **Backward compatible first** — never drop a column in the same release that stops writing to it
2. **Blue/green safe** — migrations must work while old code is still running
3. **Reversible** — every migration must have a tested rollback
4. **Observable** — log duration, row counts, and lock waits

## Migration Types

| Type | Example | Risk Level | Requires Downtime? |
|------|---------|------------|-------------------|
| Add nullable column | `ADD COLUMN foo VARCHAR(255)` | Low | No |
| Add index | `CREATE INDEX CONCURRENTLY` | Medium | No |
| Add non-null column | `ADD COLUMN foo INT NOT NULL DEFAULT 0` | Medium | No* |
| Rename column | Two-step: add new, dual-write, remove old | High | No |
| Drop column | Two-step: stop writing, then drop | High | No |
| Change data type | Add new column, backfill, swap | Critical | Yes |
| Partition table | Create new, migrate, swap | Critical | Yes |

\* Use `DEFAULT` or backfill in batches.

## Pre-Migration Checklist
- [ ] Migration script reviewed by at least one other agent/engineer
- [ ] Rollback script tested on a copy of production data
- [ ] Estimated runtime calculated (use `EXPLAIN ANALYZE` on a sample)
- [ ] Lock duration estimated; plan for low-traffic window if >5s
- [ ] Downstream consumers notified (list in `DEPENDENTS.md`)
- [ ] Backup or snapshot taken (automated or manual)
- [ ] Monitoring alerts configured for error rate spike post-migration

## Migration Script Template

```sql
-- filename: YYYYMMDD_HHMMSS_description.sql
-- author: agent-name
-- ticket: LINK-123

BEGIN;

-- Step 1: Safe operation (e.g., add nullable column)
ALTER TABLE table_name ADD COLUMN new_column TYPE;

-- Step 2: Backfill in batches if needed
-- DO NOT use a single UPDATE on large tables
-- Use a script with LIMIT and sleep(0.1)

-- Step 3: Add constraints/indexes in separate transactions if possible
-- CREATE INDEX CONCURRENTLY idx_name ON table_name(column);

COMMIT;
```

## Execution Order
1. Run migration in staging → validate
2. Run migration in production during low-traffic window
3. Verify application health (5 min of traffic)
4. Mark migration as applied in `schema_migrations` table
5. Notify all agents that schema version has changed

## Rollback Protocol
- If error rate spikes >0.1% within 10 minutes: **automatic rollback**
- If data inconsistency detected: **immediate halt + human escalation**
- Rollback script must be idempotent (safe to run twice)

## Post-Migration
- [ ] Update `schema/README.md` with new ERD or field descriptions
- [ ] Update agent prompts that reference the schema
- [ ] Archive migration file in `migrations/archived/`
- [ ] Record in `memory/YYYY-MM-DD.md`
