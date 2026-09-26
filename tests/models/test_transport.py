"""Tests for the transport seam (models/transport.py)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any, Dict

import pytest

# ----------------------------------------------------------------------
# Package import fix‑ups
# ----------------------------------------------------------------------
# The generated package expects a top‑level ``aspose_jmap_foss.common_types`` module,
# but the file lives in ``aspose_jmap_foss.models.common_types``.  Insert an alias
# so that ``import aspose_jmap_foss`` works without touching production code.
import importlib

_common_mod = importlib.import_module("aspose_jmap_foss.models.common_types")
sys.modules.setdefault("aspose_jmap_foss.common_types", _common_mod)

# Now import the public symbols from the package entry point.
from aspose_jmap_foss import (
    JmapHttpRequest,
    JmapHttpResponse,
    JmapNetworkError,
    JmapTransport,
    UrllibJmapTransport,
)


def test_jmap_http_request_defaults() -> None:
    """A request without optional fields uses the defined defaults."""
    req = JmapHttpRequest(method="POST", url="https://example.com/jmap")
    assert req.method == "POST"
    assert req.url == "https://example.com/jmap"
    # ``headers`` defaults to an empty mapping and ``body`` to ``None``.
    assert isinstance(req.headers, dict)
    assert req.headers == {}
    assert req.body is None


def test_jmap_http_response_defaults() -> None:
    """A response without optional fields uses the defined defaults."""
    resp = JmapHttpResponse(status_code=204)
    assert resp.status_code == 204
    assert isinstance(resp.headers, dict)
    assert resp.headers == {}
    assert resp.body == b""


def test_fake_transport_round_trip() -> None:
    """A hand‑written transport records the request and returns a canned response."""

    class FakeTransport(JmapTransport):
        """Simple transport that records the last request and returns a fixed response."""

        def __init__(self) -> None:
            self.last_request: JmapHttpRequest | None = None

        def send(self, request: JmapHttpRequest) -> JmapHttpResponse:
            self.last_request = request
            return JmapHttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=b'{"result":"ok"}',
            )

    transport = FakeTransport()
    request = JmapHttpRequest(
        method="POST",
        url="https://api.test/jmap",
        headers={"Accept": "application/json"},
        body=b'{"accountId":"a1","methodCalls":[]}',
    )
    response = transport.send(request)

    # Verify the request was recorded unchanged.
    assert transport.last_request is request
    assert transport.last_request.method == "POST"
    assert transport.last_request.url == "https://api.test/jmap"
    assert transport.last_request.headers == {"Accept": "application/json"}
    assert transport.last_request.body == b'{"accountId":"a1","methodCalls":[]}'

    # Verify the canned response.
    assert response.status_code == 200
    assert response.headers == {"Content-Type": "application/json"}
    assert response.body == b'{"result":"ok"}'


def test_urllib_transport_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """UrllibJmapTransport should pass the request/response body through as raw bytes,
    with no UTF-8 encode/decode round-trip (which would corrupt non-text blob content)."""

    captured: Dict[str, Any] = {}

    class DummyResponse:
        def __init__(self, status: int, headers: Dict[str, str], body: bytes) -> None:
            self._status = status
            self._headers = headers
            self._body = body

        def getcode(self) -> int:
            return self._status

        def info(self) -> Dict[str, str]:
            return self._headers

        def read(self) -> bytes:
            return self._body

        def __enter__(self) -> "DummyResponse":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401
            pass

    def fake_urlopen(req: urllib.request.Request, timeout: float = 30.0) -> DummyResponse:
        # Record the incoming request for later assertions.
        captured["method"] = req.get_method()
        captured["url"] = req.full_url
        captured["headers"] = dict(req.header_items())
        captured["data"] = req.data
        # Return a dummy JSON payload.
        body = json.dumps({"result": "ok"}).encode("utf-8")
        return DummyResponse(status=200, headers={"Content-Type": "application/json"}, body=body)

    monkeypatch.setattr(urllib.request.OpenerDirector, "open",
                        lambda self, req, timeout=30.0: fake_urlopen(req, timeout))

    transport = UrllibJmapTransport(timeout=5.0)
    request = JmapHttpRequest(
        method="POST",
        url="https://example.com/jmap",
        headers={"Accept": "application/json"},
        body=b'{"foo":"bar"}',
    )
    response = transport.send(request)

    # Verify that urllib received the request body unchanged.
    assert captured["method"] == "POST"
    assert captured["url"] == "https://example.com/jmap"
    assert captured["headers"]["Accept"] == "application/json"
    assert captured["data"] == b'{"foo":"bar"}'

    # Verify the response object - body comes back as raw bytes, not decoded.
    assert isinstance(response, JmapHttpResponse)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == json.dumps({"result": "ok"}).encode("utf-8")


def test_urllib_transport_does_not_corrupt_binary_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression test: a prior version encoded the request body as UTF-8 and decoded the
    response body as UTF-8, silently corrupting (or, for a genuinely invalid byte sequence,
    crashing on) any non-text blob content such as an image or PDF attachment. The transport
    must pass bytes straight through in both directions."""

    # A byte sequence that is not valid UTF-8 (starts like a JPEG magic number) - decoding
    # this as UTF-8 would raise UnicodeDecodeError, and re-encoding a lossy decode would not
    # round-trip back to the original bytes.
    binary_payload = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])

    captured: Dict[str, Any] = {}

    class DummyResponse:
        def __init__(self, body: bytes) -> None:
            self._body = body

        def getcode(self) -> int:
            return 200

        def info(self) -> Dict[str, str]:
            return {"Content-Type": "application/octet-stream"}

        def read(self) -> bytes:
            return self._body

        def __enter__(self) -> "DummyResponse":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401
            pass

    def fake_urlopen(req: urllib.request.Request, timeout: float = 30.0) -> DummyResponse:
        captured["data"] = req.data
        return DummyResponse(binary_payload)

    monkeypatch.setattr(urllib.request.OpenerDirector, "open",
                        lambda self, req, timeout=30.0: fake_urlopen(req, timeout))

    transport = UrllibJmapTransport(timeout=5.0)
    request = JmapHttpRequest(
        method="POST",
        url="https://example.com/upload",
        headers={"Content-Type": "application/octet-stream"},
        body=binary_payload,
    )
    response = transport.send(request)

    assert captured["data"] == binary_payload
    assert response.body == binary_payload


def test_urllib_transport_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """UrllibJmapTransport should wrap urllib errors in JmapNetworkError."""

    def raise_url_error(*_args, **_kwargs):
        raise urllib.error.URLError("simulated network failure")

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", raise_url_error)

    transport = UrllibJmapTransport()
    request = JmapHttpRequest(method="GET", url="https://unreachable.test/jmap")

    with pytest.raises(JmapNetworkError) as excinfo:
        transport.send(request)

    # The original exception message should be present in the wrapper.
    assert "simulated network failure" in str(excinfo.value)
    # Regression test: JmapNetworkError declares original_exception: Exception, but a prior
    # version passed str(exc) instead of exc itself, silently storing a str where callers
    # would reasonably expect the real exception object (e.g. to inspect its type or
    # traceback via `raise ... from`).
    assert isinstance(excinfo.value.original_exception, urllib.error.URLError)


def test_redirect_handler_strips_credentials_cross_origin() -> None:
    """Security: the custom redirect handler must drop Authorization / Cookie /
    Proxy-Authorization when a redirect crosses to a different origin, and keep every
    header on a same-origin redirect."""
    import email.message

    from aspose_jmap_foss.models.transport import _CrossOriginSafeRedirectHandler

    handler = _CrossOriginSafeRedirectHandler()

    def make_req():
        r = urllib.request.Request(
            "https://jmap.example.com/.well-known/jmap",
            headers={"Authorization": "Bearer secret", "Accept": "application/json"},
        )
        return r

    hdrs = email.message.Message()

    same = handler.redirect_request(
        make_req(), None, 307, "Temporary Redirect", hdrs,
        "https://jmap.example.com/jmap/session",
    )
    assert any(k.lower() == "authorization" for k in same.headers), "same-origin keeps auth"

    cross = handler.redirect_request(
        make_req(), None, 307, "Temporary Redirect", hdrs,
        "https://evil.example/steal",
    )
    assert not any(k.lower() == "authorization" for k in cross.headers), \
        "cross-origin must drop Authorization"
    assert any(k.lower() == "accept" for k in cross.headers), "non-credential headers stay"
