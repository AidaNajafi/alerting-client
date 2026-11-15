# Contract: alerting_client API (001)

## `AlertingClient`

```python
class AlertingClient:
    def __init__(
        self,
        webhook_url: str | None = None,
        *,
        channel: str | None = None,
        timeout: float | None = None,
        dedupe_ttl_seconds: float = 60.0,
    ) -> None: ...

    def fire(
        self,
        name: str,
        *,
        message: str = "",
        labels: dict[str, str] | None = None,
        dedupe: bool = True,
        raise_on_error: bool = False,
    ) -> dict: ...
```

### `fire` return value

```json
{
  "ok": true,
  "skipped": false,
  "reason": null,
  "status_code": 200
}
```

When skipped (no URL or deduped):

```json
{
  "ok": true,
  "skipped": true,
  "reason": "no_webhook_url" | "deduped",
  "status_code": null
}
```

When fail-soft error:

```json
{
  "ok": false,
  "skipped": false,
  "reason": "http_error" | "network_error",
  "status_code": 500
}
```

## HTTP request

- Method: `POST`
- URL: webhook URL
- Body: `{"text": "<markdown-ish plain text>", "channel": "<optional>"}`
- `text` MUST contain alert `name`, `message`, and each label as `` `key`=`value` `` lines.
