# Specs constitution — alerting-client

This tree follows Spec Kit (`spec.md` → `plan.md` → `tasks.md`).

## Principles

1. **Public OSS** — No secrets, tokens, or company webhook URLs in the repository.
2. **Notify-only in v1** — The library sends notifications; it does not own ACK or escalation.
3. **App-owned secrets** — Callers configure delivery via environment variables.
4. **Fail soft** — Notification failures MUST NOT crash the host application by default.
5. **No Grafana coupling** — This package MUST NOT depend on Grafana, Prometheus, or any metrics alert pipeline.
6. **Future ACK** — Escalation/ACK MAY appear as a later feature (`002-…`) without changing the Grafana-as-code product.

## Features

| ID | Name | Status |
|----|------|--------|
| 001 | Notify client | Spec / implement |
| 002 | ACK escalation | Deferred |

## Product truth

Canonical behavior lives under `specs/`. README must stay aligned with accepted specs.
