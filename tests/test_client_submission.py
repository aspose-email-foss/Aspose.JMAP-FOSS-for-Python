"""Tests for the submission client mixin (public JmapClient)."""

from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest

from aspose_jmap_foss import (
    JmapClient,
    JmapClientOptions,
    JmapTransport,
    JmapHttpRequest,
    JmapHttpResponse,
)
from aspose_jmap_foss.models.email_submission import EmailSubmission
from aspose_jmap_foss.models.common_types import JmapProtocolError


class FakeJmapTransport(JmapTransport):
    """A fake transport that returns pre‑programmed responses and records the request."""

    def __init__(self, responses: List[JmapHttpResponse]) -> None:
        self._responses = iter(responses)
        self.last_request: JmapHttpRequest | None = None

    def send(self, request: JmapHttpRequest) -> JmapHttpResponse:
        self.last_request = request
        try:
            return next(self._responses)
        except StopIteration as exc:  # pragma: no cover
            raise RuntimeError("No more fake responses configured") from exc


def make_session_response() -> JmapHttpResponse:
    """Return a fake response containing a minimal Session JSON."""
    session_json = {
        "apiUrl": "https://example.com/api",
        "downloadUrl": "https://example.com/download/{accountId}/{blobId}/{type}/{name}",
        "uploadUrl": "https://example.com/upload/{accountId}",
        "accounts": {"u1": {}},
        "primaryAccounts": {"submission": "u1"},
        "username": "user@example.test",
        "capabilities": {},
        "eventSourceUrl": "https://example.com/eventsource/",
        "state": "0",
    }
    return JmapHttpResponse(status_code=200, body=json.dumps(session_json))


def test_send_success() -> None:
    """Happy‑path test for ``JmapClient.send``."""
    # Prepare the EmailSubmission payload.
    email_sub = EmailSubmission(identity_id="id1", email_id="e1")
    create_payload = {"c1": email_sub}

    # Fake responses: first the session, then the method response.
    method_response = {
        "sessionState": "0",
        "methodResponses": [
            [
                "EmailSubmission/set",
                {
                    "accountId": "u1",
                    "newState": "1",
                    "created": {
                        "c1": {
                            "id": "sub1",
                            "sendAt": "2026-08-18T10:00:00Z",
                            "undoStatus": "final",
                        }
                    },
                },
                "c1",
            ]
        ],
    }
    transport = FakeJmapTransport(
        responses=[make_session_response(), JmapHttpResponse(status_code=200, body=json.dumps(method_response))]
    )

    options = JmapClientOptions(
        session_url="https://example.com/.well-known/jmap",
        username="user",
        password="secret",
        transport=transport,
    )
    with JmapClient(options) as client:
        client.connect()
        result = client.send(account_id="u1", create=create_payload)

    # Verify the request body.
    assert transport.last_request is not None
    req_body = json.loads(transport.last_request.body)
    assert req_body["using"] == ["urn:ietf:params:jmap:submission"]
    method_call = req_body["methodCalls"][0]
    assert method_call[0] == "EmailSubmission/set"
    args = method_call[1]
    assert args["accountId"] == "u1"
    assert args["create"]["c1"] == email_sub.to_json()

    # Verify the returned data.
    assert "created" in result
    assert result["created"]["c1"]["id"] == "sub1"


def test_list_submissions_edge_case() -> None:
    """Test ``list_submissions`` with no optional arguments and an empty result."""
    method_response = {
        "sessionState": "0",
        "methodResponses": [
            [
                "EmailSubmission/get",
                {
                    "accountId": "u1",
                    "state": "state0",
                    "list": [],
                    "notFound": [],
                },
                "c1",
            ]
        ],
    }
    transport = FakeJmapTransport(
        responses=[make_session_response(), JmapHttpResponse(status_code=200, body=json.dumps(method_response))]
    )

    options = JmapClientOptions(
        session_url="https://example.com/.well-known/jmap",
        username="user",
        password="secret",
        transport=transport,
    )
    with JmapClient(options) as client:
        client.connect()
        result = client.list_submissions(account_id="u1")

    # Verify request arguments.
    assert transport.last_request is not None
    req_body = json.loads(transport.last_request.body)
    method_call = req_body["methodCalls"][0]
    assert method_call[0] == "EmailSubmission/get"
    args = method_call[1]
    assert args["accountId"] == "u1"
    # No optional fields should be present.
    assert "ids" not in args
    assert "properties" not in args

    # Verify the empty list result.
    assert result["list"] == []


def test_send_protocol_error_raises() -> None:
    """Ensure a protocol‑level error response raises ``JmapProtocolError``."""
    error_response = {
        "sessionState": "0",
        "methodResponses": [
            ["error", {"type": "unknownMethod", "description": "Method not supported"}, "c1"]
        ],
    }
    transport = FakeJmapTransport(
        responses=[make_session_response(), JmapHttpResponse(status_code=200, body=json.dumps(error_response))]
    )

    options = JmapClientOptions(
        session_url="https://example.com/.well-known/jmap",
        username="user",
        password="secret",
        transport=transport,
    )
    with JmapClient(options) as client:
        client.connect()
        with pytest.raises(JmapProtocolError) as excinfo:
            client.send(account_id="u1", create={"c1": EmailSubmission(identity_id="id1", email_id="e1")})
    assert excinfo.value.type == "unknownMethod"
    assert "Method not supported" in str(excinfo.value)
