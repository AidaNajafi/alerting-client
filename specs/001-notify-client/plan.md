# Implementation Plan: Notify-only alerting client

**Branch**: `001-notify-client` | **Date**: 2026-11-15 | **Spec**: [spec.md](./spec.md)

## Summary

Ship a minimal Poetry/setuptools Python package `alerting-client` that POSTs Mattermost-compatible webhook payloads. Configuration via environment variables only. Unit-tested without live Mattermost.

## Technical Context

**Language**: Python ≥3.10  
**Dependencies**: `httpx`  
**Testing**: pytest  
**Distribution**: GitHub public repo; installable via `pip install git+https://…` or PyPI later  
**Platform**: any OS with outbound HTTPS  

## Constitution Check

| Gate | Status |
|------|--------|
| No secrets in repo | Pass |
| Notify-only | Pass |
| No Grafana coupling | Pass |

## Project Structure

```text
alerting-client/
  pyproject.toml
  README.md
  LICENSE
  .gitignore
  src/alerting_client/
    __init__.py
    client.py
  tests/
    test_client.py
  specs/
    constitution.md
    001-notify-client/
```

## API

See [contracts/api.md](./contracts/api.md).

## Env

| Variable | Required | Default |
|----------|----------|---------|
| `ALERTING_WEBHOOK_URL` | for send | unset → skip |
| `ALERTING_CHANNEL` | no | omit channel field |
| `ALERTING_TIMEOUT_SECONDS` | no | `10` |

## Complexity

Low. Single module + tests.
