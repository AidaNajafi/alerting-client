# Feature Specification: Notify-only alerting client

**Feature Branch**: `001-notify-client`  
**Created**: 2026-11-15  
**Status**: Accepted (plan-approved)  
**Input**: Open-source Python library that apps call to send alerts to Mattermost (or a generic webhook). No ACK/escalation in v1. No Grafana coupling.

## Clarifications

### Session 2026-11-15

- Q: Delivery target? → A: Incoming webhook URL from env (Mattermost-compatible JSON `text` body; same URL works for generic webhooks that accept JSON).
- Q: ACK / manager→employee? → A: Out of scope for 001; deferred to later feature.
- Q: Shared brain with Grafana? → A: No. Completely separate from grafana-alerting.
- Q: Secrets in repo? → A: Never. Callers set env vars.

## User Scenarios & Testing

### User Story 1 - Fire an alert from application code (Priority: P1)

A developer installs the package and calls `fire` when something bad happens (e.g. live websocket disconnect). A message appears in the configured Mattermost channel (or webhook endpoint).

**Why this priority**: Core value of the package.

**Independent Test**: Set `ALERTING_WEBHOOK_URL` to a test webhook; call `fire`; observe HTTP 2xx and payload shape.

**Acceptance Scenarios**:

1. **Given** `ALERTING_WEBHOOK_URL` is set to a reachable webhook, **When** the app calls `fire(name="x", message="y")`, **Then** the library POSTs JSON including a human-readable text body and returns success metadata without raising.
2. **Given** labels `{"component":"tadbir"}`, **When** `fire` is called, **Then** those labels appear in the message text (and optional structured field).
3. **Given** no webhook URL is configured, **When** `fire` is called, **Then** the library does not raise by default; it logs/skips (or returns a skipped result).

---

### User Story 2 - Fail soft (Priority: P1)

Network or webhook errors must not take down the host process.

**Independent Test**: Point URL at a closed port; call `fire`; process continues; error is surfaced as return value or log.

**Acceptance Scenarios**:

1. **Given** the webhook is unreachable, **When** `fire` runs with default options, **Then** no uncaught exception escapes to the caller.
2. **Given** the caller sets `raise_on_error=True`, **When** the webhook fails, **Then** an exception is raised.

---

### User Story 3 - Optional simple dedupe (Priority: P2)

Rapid repeated fires with the same name+labels should not spam the webhook within a short window (process-local).

**Independent Test**: Call `fire` twice quickly with identical name/labels; only one HTTP POST within the TTL.

**Acceptance Scenarios**:

1. **Given** dedupe enabled (default), **When** two identical fires occur within the TTL, **Then** only the first sends HTTP.
2. **Given** dedupe disabled, **When** two identical fires occur, **Then** both send HTTP.

---

## Requirements

### Functional

- **FR-001**: Package name `alerting-client`; import `alerting_client`.
- **FR-002**: Public API `AlertingClient.fire(name, message="", labels=None, *, dedupe=True, raise_on_error=False)`.
- **FR-003**: Read `ALERTING_WEBHOOK_URL` (required for send); optional `ALERTING_CHANNEL` for Mattermost channel slug override; optional `ALERTING_TIMEOUT_SECONDS` (default 10).
- **FR-004**: POST JSON body at least `{"text": "..."}`; if channel set, include `"channel"`.
- **FR-005**: Message text MUST include alert name, message, and labels.
- **FR-006**: No dependency on Grafana, Prometheus, or a company “brain” service.
- **FR-007**: Process-local dedupe key = hash(name + sorted labels); default TTL 60s.

### Non-goals (001)

- ACK, escalation, slash commands, WebSocket listeners.
- Persistent alert store / database.
- Multi-backend routing (Slack, PagerDuty) — may come later.

## Success Criteria

- SC-001: A new project can `pip`/`poetry` install and send a Mattermost message with under 10 lines of code.
- SC-002: Unit tests cover payload shape, skip-when-unset, fail-soft, and dedupe without network.
- SC-003: README documents env vars and that ACK is out of scope.
