"""Tests for the core client mixin (exposed via the public JmapClient)."""

from __future__ import annotations

import json
import uuid
from typing import Callable, List
from urllib.parse import quote

import pytest

from aspose_jmap_foss import (
    Invocation,
    JmapClient,
    JmapClientOptions,
    JmapTransport,
    JmapHttpRequest,
    JmapHttpResponse,
    JmapProtocolError,
    ResultReference,
)


class CallbackTransport(JmapTransport):
    """Transport that delegates response generation to a user‑provided callback."""

    def __init__(self, handler: Callable[[JmapHttpRequest], JmapHttpResponse]) -> None:
        self._handler = handler
        self.requests: List[JmapHttpRequest] = []

    def send(self, request: JmapHttpRequest) -> JmapHttpResponse:
        self.requests.append(request)
        return self._handler(request)


# Minimal session JSON required by the client implementation.
SESSION_JSON = {
    "capabilities": {"urn:ietf:params:jmap:core": {}},
    "accounts": {"u1": {}},
    "primaryAccounts": {"urn:ietf:params:jmap:core": "u1"},
    "username": "user@example.test",
    "apiUrl": "https://example.com/api",
    "uploadUrl": "https://example.com/upload/{accountId}",
    "downloadUrl": "https://example.com/download/{accountId}/{blobId}/{type}/{name}",
    "eventSourceUrl": "https://example.com/eventsource/",
    "state": "s1",
}


def make_options(transport: JmapTransport) -> JmapClientOptions:
    return JmapClientOptions(
        session_url="https://example.com/.well-known/jmap",
        username="user",
        password="pass",
        transport=transport,
    )


def test_connect_fetches_session_and_sets_auth_header():
    """connect() must GET the session URL and return a Session object."""
    def handler(req: JmapHttpRequest) -> JmapHttpResponse:
        assert req.method == "GET"
        assert req.url == "https://example.com/.well-known/jmap"
        assert req.headers.get("Authorization") == "Basic " + (
            "user:pass".encode().hex()
        ) or req.headers.get("Authorization").startswith("Basic ")
        return JmapHttpResponse(200, {}, json.dumps(SESSION_JSON))

    transport = CallbackTransport(handler)
    client = JmapClient(make_options(transport))

    with client as c:
        session = c.connect()
        # Verify that the returned Session contains the expected API URL.
        assert hasattr(session, "api_url")
        assert session.api_url == SESSION_JSON["apiUrl"]
        # Ensure exactly one request was made.
        assert len(transport.requests) == 1


def test_connect_uses_bearer_token_when_set():
    """When bearer_token is set, the Authorization header must be 'Bearer <token>' instead
    of HTTP Basic auth, even though username/password are also provided."""
    def handler(req: JmapHttpRequest) -> JmapHttpResponse:
        assert req.headers.get("Authorization") == "Bearer my-oauth-token"
        return JmapHttpResponse(200, {}, json.dumps(SESSION_JSON))

    transport = CallbackTransport(handler)
    options = JmapClientOptions(
        session_url="https://example.com/.well-known/jmap",
        username="user",
        password="pass",
        bearer_token="my-oauth-token",
        transport=transport,
    )
    client = JmapClient(options)

    with client as c:
        c.connect()
        assert len(transport.requests) == 1


def test_echo_returns_arguments_and_uses_correct_call_id():
    """echo() must send a Core/echo invocation and return the echoed arguments."""
    account_id = "A1"
    arguments = {"hello": True, "high": 5}

    def handler(req: JmapHttpRequest) -> JmapHttpResponse:
        if req.method == "GET":
            return JmapHttpResponse(200, {}, json.dumps(SESSION_JSON))
        # POST to the API URL for the echo method.
        assert req.method == "POST"
        assert req.url == SESSION_JSON["apiUrl"]
        payload = json.loads(req.body)
        # Verify the using list contains the core capability.
        assert "urn:ietf:params:jmap:core" in payload.get("using", [])
        # echo() uses a fixed literal call-id ("c1"), since it only ever sends one call.
        call_id = payload["methodCalls"][0][2]
        assert call_id == "c1"
        # Echo back the same arguments.
        resp = {
            "methodResponses": [
                ["Core/echo", payload["methodCalls"][0][1], call_id]
            ],
            "sessionState": "s1",
        }
        return JmapHttpResponse(200, {}, json.dumps(resp))

    transport = CallbackTransport(handler)

    client = JmapClient(make_options(transport))

    with client as c:
        c.connect()
        result = c.echo(account_id, arguments)
        assert result == arguments
        # Two requests: session GET and echo POST.
        assert len(transport.requests) == 2
        echo_req = transport.requests[1]
        assert echo_req.method == "POST"
        assert echo_req.headers["Content-Type"] == "application/json"


def test_upload_blob_returns_parsed_response():
    """upload_blob() must POST to the upload URL and return parsed JSON, sending the raw
    bytes verbatim - not lossily re-encoded as UTF-8, which would corrupt real (non-text)
    attachment content such as an image."""
    account_id = "A2"
    # Not valid UTF-8 (starts like a JPEG magic number) - a prior version decoded this as
    # UTF-8 with errors="ignore", silently dropping/altering bytes before sending.
    data = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])
    content_type = "image/jpeg"
    upload_response = {
        "accountId": account_id,
        "blobId": "blob123",
        "type": content_type,
        "size": len(data),
    }

    def handler(req: JmapHttpRequest) -> JmapHttpResponse:
        if req.method == "GET":
            return JmapHttpResponse(200, {}, json.dumps(SESSION_JSON))
        # POST to the formatted upload URL (accountId percent-encoded).
        expected_url = SESSION_JSON["uploadUrl"].format(accountId=quote(account_id, safe=""))
        assert req.method == "POST"
        assert req.url == expected_url
        assert req.headers["Content-Type"] == content_type
        # The raw bytes must be sent verbatim, with no lossy UTF-8 round-trip.
        assert req.body == data
        return JmapHttpResponse(200, {}, json.dumps(upload_response))

    transport = CallbackTransport(handler)

    client = JmapClient(make_options(transport))

    with client as c:
        c.connect()
        result = c.upload_blob(account_id, data, content_type)
        assert result == upload_response
        # Two requests: session GET and upload POST.
        assert len(transport.requests) == 2


def test_download_blob_returns_bytes():
    """download_blob() must GET the download URL and return the body as bytes, verbatim -
    not run through a UTF-8 decode/re-encode round-trip, which would corrupt (or, for a
    genuinely invalid byte sequence, crash on) real non-text attachment content."""
    account_id = "A3"
    blob_id = "blob456"
    type_ = "application/octet-stream"
    name = "file.bin"
    # Not valid UTF-8 (starts like a JPEG magic number).
    raw_body = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])

    def handler(req: JmapHttpRequest) -> JmapHttpResponse:
        if req.method == "GET" and req.url == "https://example.com/.well-known/jmap":
            return JmapHttpResponse(200, {}, json.dumps(SESSION_JSON))
        # GET to the formatted download URL (each segment percent-encoded).
        expected_url = SESSION_JSON["downloadUrl"].format(
            accountId=quote(account_id, safe=""),
            blobId=quote(blob_id, safe=""),
            type=quote(type_, safe=""),
            name=quote(name, safe=""),
        )
        assert req.method == "GET"
        assert req.url == expected_url
        return JmapHttpResponse(200, {}, raw_body)

    transport = CallbackTransport(handler)

    client = JmapClient(make_options(transport))

    with client as c:
        c.connect()
        result = c.download_blob(account_id, blob_id, type_, name)
        assert result == raw_body
        # Two requests: session GET and download GET.
        assert len(transport.requests) == 2


def test_upload_and_download_blob_percent_encode_url_segments():
    """Regression test: account_id/blob_id/type/name are spliced verbatim into a URL path
    segment. A value containing "/", "?", or "#" must be percent-encoded, or it would
    rewrite the request path or smuggle extra query parameters into the request."""
    account_id = "a/b"
    blob_id = "blob#1?x=1"

    def handler(req: JmapHttpRequest) -> JmapHttpResponse:
        if req.method == "GET" and req.url == "https://example.com/.well-known/jmap":
            return JmapHttpResponse(200, {}, json.dumps(SESSION_JSON))
        if req.method == "POST":
            assert req.url == "https://example.com/upload/a%2Fb"
            return JmapHttpResponse(
                200, {}, json.dumps({"accountId": account_id, "blobId": "b1", "type": "text/plain", "size": 1})
            )
        # download GET
        assert req.url == "https://example.com/download/a%2Fb/blob%231%3Fx%3D1/text%2Fplain/na%2Fme"
        return JmapHttpResponse(200, {}, b"x")

    transport = CallbackTransport(handler)
    client = JmapClient(make_options(transport))

    with client as c:
        c.connect()
        c.upload_blob(account_id, b"x", "text/plain")
        c.download_blob(account_id, blob_id, "text/plain", "na/me")


def test_echo_propagates_protocol_error():
    """If the response contains an \"error\" invocation, echo() must raise JmapProtocolError."""
    account_id = "A4"
    arguments = {"test": 1}

    def handler(req: JmapHttpRequest) -> JmapHttpResponse:
        if req.method == "GET":
            return JmapHttpResponse(200, {}, json.dumps(SESSION_JSON))
        # Return an error invocation for the echo call.
        resp = {
            "methodResponses": [
                ["error", {"type": "unknownMethod", "description": "bad method"}, "c1"]
            ],
            "sessionState": "s1",
        }
        return JmapHttpResponse(200, {}, json.dumps(resp))

    transport = CallbackTransport(handler)

    client = JmapClient(make_options(transport))

    with client as c:
        c.connect()
        with pytest.raises(JmapProtocolError) as excinfo:
            c.echo(account_id, arguments)
        err = excinfo.value
        assert err.type == "unknownMethod"
        assert err.description == "bad method"
        # Two requests: session GET and echo POST.
        assert len(transport.requests) == 2


def test_send_request_batches_multiple_calls_with_a_result_reference():
    """send_request() must be public (not the private _send_request it replaced), so callers
    can batch multiple method calls - chained via a ResultReference back-reference (RFC 8620
    section 3.7) - into a single HTTP round trip instead of one request per call.
    """

    def handler(req: JmapHttpRequest) -> JmapHttpResponse:
        if req.method == "GET":
            return JmapHttpResponse(200, {}, json.dumps(SESSION_JSON))
        payload = json.loads(req.body)
        calls = payload["methodCalls"]
        # Exactly one HTTP request carrying both calls.
        assert len(calls) == 2
        assert calls[0][2] == "c1"
        assert calls[1][2] == "c2"
        # The second call's arguments reference the first call's result via a "#"-prefixed key.
        assert calls[1][1]["#foo"] == {
            "resultOf": "c1",
            "name": "Core/echo",
            "path": "/hello",
        }
        resp = {
            "methodResponses": [
                ["Core/echo", {"hello": "world"}, "c1"],
                ["Core/echo", {"foo": "world"}, "c2"],
            ],
            "sessionState": "s1",
        }
        return JmapHttpResponse(200, {}, json.dumps(resp))

    transport = CallbackTransport(handler)
    client = JmapClient(make_options(transport))

    with client as c:
        c.connect()
        first = Invocation(name="Core/echo", arguments={"hello": "world"}, method_call_id="c1")
        second = Invocation(
            name="Core/echo",
            # Invocation.arguments values must already be JSON-compatible (Invocation.to_json()
            # returns them verbatim) - so the ResultReference is serialized here, not passed as
            # a raw model instance.
            arguments={"#foo": ResultReference(result_of="c1", name="Core/echo", path="/hello").to_json()},
            method_call_id="c2",
        )
        resp_env = c.send_request([first, second], using=["urn:ietf:params:jmap:core"])

        assert len(resp_env.method_responses) == 2
        assert resp_env.method_responses[0].arguments == {"hello": "world"}
        assert resp_env.method_responses[1].arguments == {"foo": "world"}
        # Session GET + exactly one batched POST (not two).
        assert len(transport.requests) == 2
