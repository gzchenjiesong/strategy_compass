---
title: Monitoring and Alerting SOP
type: sop
created: 2026-05-13
tags: [observability, alerting, on-call]
---

# Monitoring Setup and Alert Handling

## Purpose
Ensure system health is visible, anomalies are detected quickly, and alerts lead to actionable responses—not noise.

## Monitoring Layers

| Layer | What to Monitor | Tool Example |
|-------|-----------------|--------------|
| Infrastructure | CPU, memory, disk, network | Prometheus + Node Exporter |
| Application | Error rate, latency, throughput | Prometheus + custom metrics |
| Business | Daily active users, conversion rate | Metabase / custom dashboard |
| Data Pipeline | Job success rate, lag, schema drift | Airflow / custom checks |
| Security | Failed logins, anomaly traffic | WAF logs + SIEM |

## Golden Signals (per service)
1. **Latency** — p50, p95, p99 response times
2. **Traffic** — requests per second
3. **Errors** — rate of 5xx / failed jobs
4. **Saturation** — CPU, memory, connection pool usage

## Alerting Rules

### Severity Levels
| Severity | Condition | Notification Channel | Response SLA |
|----------|-----------|----------------------|--------------|
| P0 (Page) | Service down, data loss, security incident | SMS + Phone + Slack | 5 minutes |
| P1 (Urgent) | Error rate >1%, latency p99 >2x baseline | Slack + Email | 30 minutes |
| P2 (Warning) | Error rate >0.1%, disk >80% | Slack only | 4 hours |
| P3 (Info) | Anomaly detected, non-critical job failed | Dashboard + weekly digest | Next business day |

### Alert Quality Standards
- [ ] Every alert has a runbook link
- [ ] Alert triggers only when human action is required
- [ ] Alert includes: what, where, when, impact, suggested action
- [ ] No alert fires for <5 minutes (avoid flapping)
- [ ] Auto-resolve when metric returns to normal

## Runbook Template

```markdown
# Alert: <AlertName>

## Symptoms
<What the user sees>

## Diagnosis Steps
1. Check <dashboard link>
2. Check logs: `kubectl logs -f deployment/<service>`
3. Check recent deployments: `git log --since="1 hour ago"`

## Common Causes
- Cause A → Fix A
- Cause B → Fix B

## Escalation
If unresolved in <SLA>, escalate to <person/team>
```

## Alert Handling Workflow

1. **Acknowledge** — claim the alert within SLA to prevent escalation
2. **Assess** — confirm it's a real issue (not a false positive)
3. **Mitigate** — apply the fastest fix to restore service (not root cause)
4. **Investigate** — after mitigation, find root cause
5. **Document** — update runbook or create a post-mortem
6. **Improve** — add a test or monitoring to prevent recurrence

## On-Call Rotation
- Primary: responds to P0/P1
- Secondary: backup, handles P2 if primary is busy
- Escalation: human lead if both unavailable

## Dashboard Standards
- Default time range: last 6 hours
- Key metrics at the top; drill-down below
- Annotations for deployments and incidents
- Shared URL in runbook

## Noise Reduction
- Review all alerts monthly; retire any with >20% false-positive rate
- Use SLO-based alerting (burn rate) instead of static thresholds where possible
- Aggregate similar alerts; avoid one alert per host
