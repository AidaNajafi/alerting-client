from __future__ import annotations

import httpx
import pytest

from alerting_client import AlertingClient
from alerting_client import client as client_mod


@pytest.fixture(autouse=True)
def _clear_dedupe():
    client_mod._dedupe_until.clear()
    yield
    client_mod._dedupe_until.clear()


def test_skip_when_no_webhook():
    c = AlertingClient(webhook_url="")
    result = c.fire("test_alert", message="hi")
    assert result["ok"] is True
    assert result["skipped"] is True
    assert result["reason"] == "no_webhook_url"


def test_payload_and_success(monkeypatch):
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["json"] = httpx.Response(200).json if False else None
        import json

        seen["body"] = json.loads(request.content.decode())
        return httpx.Response(200, text="ok")

    transport = httpx.MockTransport(handler)
    c = AlertingClient(
        webhook_url="https://example.com/hooks/x",
        channel="alert-system",
        timeout=5,
    )

    real_client = httpx.Client

    def fake_client(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", fake_client)
    result = c.fire(
        "emam_live_ws_disconnect",
        message="disconnected",
        labels={"component": "tadbir"},
    )
    assert result["ok"] is True
    assert result["skipped"] is False
    assert seen["body"]["channel"] == "alert-system"
    assert "emam_live_ws_disconnect" in seen["body"]["text"]
    assert "tadbir" in seen["body"]["text"]


def test_dedupe(monkeypatch):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, text="ok")

    transport = httpx.MockTransport(handler)
    real_client = httpx.Client

    def fake_client(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", fake_client)
    c = AlertingClient(webhook_url="https://example.com/hooks/x", dedupe_ttl_seconds=60)
    assert c.fire("a", labels={"k": "v"})["skipped"] is False
    assert c.fire("a", labels={"k": "v"})["reason"] == "deduped"
    assert calls["n"] == 1


def test_fail_soft(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="nope")

    transport = httpx.MockTransport(handler)
    real_client = httpx.Client

    def fake_client(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", fake_client)
    c = AlertingClient(webhook_url="https://example.com/hooks/x")
    result = c.fire("x", raise_on_error=False)
    assert result["ok"] is False
    assert result["reason"] == "http_error"
