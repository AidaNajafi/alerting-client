from __future__ import annotations

import hashlib
import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger("alerting_client")

_dedupe_until: dict[str, float] = {}


def _dedupe_key(name: str, labels: dict[str, str]) -> str:
    label_part = ",".join(f"{k}={labels[k]}" for k in sorted(labels))
    raw = f"{name}|{label_part}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _format_text(name: str, message: str, labels: dict[str, str]) -> str:
    lines = [f"**[{name}]**"]
    if message.strip():
        lines.append(message.strip())
    for key in sorted(labels):
        lines.append(f"**{key}:** `{labels[key]}`")
    return "\n".join(lines)


class AlertingClient:
    """Send notify-only alerts to a Mattermost-compatible incoming webhook."""

    def __init__(
        self,
        webhook_url: str | None = None,
        *,
        channel: str | None = None,
        timeout: float | None = None,
        dedupe_ttl_seconds: float = 60.0,
    ) -> None:
        self.webhook_url = (
            webhook_url
            if webhook_url is not None
            else (os.getenv("ALERTING_WEBHOOK_URL") or "").strip()
        )
        self.channel = (
            channel
            if channel is not None
            else (os.getenv("ALERTING_CHANNEL") or "").strip()
        )
        if timeout is not None:
            self.timeout = timeout
        else:
            raw = os.getenv("ALERTING_TIMEOUT_SECONDS", "10")
            try:
                self.timeout = float(raw)
            except ValueError:
                self.timeout = 10.0
        self.dedupe_ttl_seconds = dedupe_ttl_seconds

    def fire(
        self,
        name: str,
        *,
        message: str = "",
        labels: dict[str, Any] | None = None,
        dedupe: bool = True,
        raise_on_error: bool = False,
    ) -> dict[str, Any]:
        """POST an alert to the configured webhook.

        Returns a result dict. By default never raises (fail-soft).
        """
        clean_labels = {
            str(k): str(v) for k, v in (labels or {}).items() if v is not None
        }

        if not self.webhook_url:
            logger.warning("ALERTING_WEBHOOK_URL unset — skip fire name=%s", name)
            return {
                "ok": True,
                "skipped": True,
                "reason": "no_webhook_url",
                "status_code": None,
            }

        if dedupe:
            key = _dedupe_key(name, clean_labels)
            now = time.monotonic()
            until = _dedupe_until.get(key, 0.0)
            if now < until:
                return {
                    "ok": True,
                    "skipped": True,
                    "reason": "deduped",
                    "status_code": None,
                }
            _dedupe_until[key] = now + self.dedupe_ttl_seconds

        payload: dict[str, Any] = {
            "text": _format_text(name, message, clean_labels),
        }
        if self.channel:
            payload["channel"] = self.channel.lstrip("#")

        try:
            with httpx.Client(timeout=self.timeout, trust_env=False) as client:
                response = client.post(self.webhook_url, json=payload)
            if response.is_error:
                result = {
                    "ok": False,
                    "skipped": False,
                    "reason": "http_error",
                    "status_code": response.status_code,
                }
                if raise_on_error:
                    response.raise_for_status()
                logger.error(
                    "webhook failed status=%s body=%s",
                    response.status_code,
                    response.text[:200],
                )
                return result
            return {
                "ok": True,
                "skipped": False,
                "reason": None,
                "status_code": response.status_code,
            }
        except Exception as exc:
            logger.exception("webhook request failed name=%s", name)
            if raise_on_error:
                raise
            return {
                "ok": False,
                "skipped": False,
                "reason": "network_error",
                "status_code": None,
                "error": str(exc),
            }
