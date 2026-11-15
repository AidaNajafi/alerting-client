# alerting-client

**Notify-only** Python library for application alerts (Mattermost-compatible incoming webhooks).

- **Not** Grafana / Prometheus
- **Not** ACK / escalation (planned as a later feature)
- **No secrets** in this repository — configure via environment

## Install

```bash
pip install "git+https://github.com/<org>/alerting-client.git"
# or after PyPI publish:
# pip install alerting-client
```

Poetry:

```bash
poetry add "git+https://github.com/<org>/alerting-client.git"
```

## Usage

```bash
export ALERTING_WEBHOOK_URL="https://chat.example.com/hooks/...."
export ALERTING_CHANNEL="alert-system"   # optional
```

```python
from alerting_client import AlertingClient

AlertingClient().fire(
    "emam_live_ws_disconnect",
    message="live websocket disconnected",
    labels={"component": "tadbir"},
)
```

## Environment

| Variable | Meaning |
|----------|---------|
| `ALERTING_WEBHOOK_URL` | Incoming webhook URL (required to send) |
| `ALERTING_CHANNEL` | Optional Mattermost channel slug |
| `ALERTING_TIMEOUT_SECONDS` | HTTP timeout (default 10) |

If the webhook URL is unset, `fire` skips and returns `skipped=True` (does not crash the app).

## Specs

See `specs/constitution.md` and `specs/001-notify-client/`.

## License

MIT
