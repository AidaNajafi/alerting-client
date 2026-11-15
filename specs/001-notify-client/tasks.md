# Tasks: Notify-only alerting client

**Input**: spec.md, plan.md, contracts/api.md

## Phase 1: Setup

- [x] T001 Create `pyproject.toml` for package `alerting-client` (httpx, pytest)
- [x] T002 Add `.gitignore`, `LICENSE` (MIT), `README.md` aligned with spec
- [x] T003 Create package layout `src/alerting_client/`

## Phase 2: Implementation

- [x] T004 Implement `AlertingClient` per contracts/api.md in `src/alerting_client/client.py`
- [x] T005 Export from `src/alerting_client/__init__.py`
- [x] T006 Process-local dedupe (name + labels, TTL)

## Phase 3: Tests & polish

- [x] T007 Unit tests with httpx mock transport: payload, skip, fail-soft, dedupe
- [x] T008 Run pytest green
- [x] T009 README: install, env vars, example, non-goals (ACK/Grafana)
