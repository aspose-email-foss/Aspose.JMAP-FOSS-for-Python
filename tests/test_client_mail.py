"""Tests for the Mail client mixin (public JmapClient)."""

from __future__ import annotations

import json
from typing import Dict, List

import pytest

from aspose_jmap_foss import (
    JmapClient,
    JmapClientOptions,
    JmapTransport,
    JmapHttpRequest,
    JmapHttpResponse,
    JmapProtocolError,
)


class FakeJmapTransport(JmapTransport):
    """A minimal transport that returns pre‑canned responses and records the last request."""

    def __init__(
        self,
        session_response: JmapHttpResponse,
        method_response: JmapHttpResponse,
    ) -> None:
        self._session_response = session_response
        self._method_response = method_response
        self.last_request: JmapHttpRequest | None = None

    def send(self, request: JmapHttpRequest) -> JmapHttpResponse:
        self.last_request = request
        if request.method == "GET":
            return self._session_response
        return self._method_response


def _make_session_response() -> JmapHttpResponse:
    """Create a minimal but valid Session JSON response."""
    session_json = {
        "capabilities": {"urn:ietf:params:jmap:mail": {}},
        "accounts": {"u1": {}},
        "primaryAccounts": {"urn:ietf:params:jmap:mail": "u1"},
        "username": "user@example.test",
        "apiUrl": "https://jmap.example.com/api",
        "downloadUrl": "https://jmap.example.com/download/{accountId}/{blobId}/{type}/{name}",
        "uploadUrl": "https://jmap.example.com/upload/{accountId}",
        "eventSourceUrl": "https://jmap.example.com/eventsource/",
        "state": "test",
    }
    return JmapHttpResponse(
        status_code=200,
        headers={},
        body=json.dumps(session_json),
    )


def _make_method_response(method_name: str, arguments: Dict) -> JmapHttpResponse:
    """Wrap a single method response in a JMAP envelope."""
    envelope = {
        "sessionState": "test",
        "methodResponses": [[method_name, arguments, "c1"]],
    }
    return JmapHttpResponse(
        status_code=200,
        headers={},
        body=json.dumps(envelope),
    )


def test_list_mailboxes_success() -> None:
    """list_mailboxes returns Mailbox objects and issues the correct request."""
    # Arrange – fake transport with session and method responses
    session_resp = _make_session_response()
    mailbox_json = {
        "id": "mb1",
        "name": "Inbox",
        "parentId": None,
        "role": "inbox",
        "sortOrder": 0,
        "totalEmails": 3,
        "unreadEmails": 1,
        "totalThreads": 3,
        "unreadThreads": 1,
        "myRights": {
            "mayReadItems": True,
            "mayAddItems": True,
            "mayRemoveItems": True,
            "maySetSeen": True,
            "maySetKeywords": True,
            "mayCreateChild": True,
            "mayRename": False,
            "mayDelete": False,
            "maySubmit": True,
        },
        "isSubscribed": True,
    }
    method_resp = _make_method_response(
        "Mailbox/get",
        {
            "accountId": "u1",
            "state": "1",
            "list": [mailbox_json],
            "notFound": [],
        },
    )
    transport = FakeJmapTransport(session_resp, method_resp)

    options = JmapClientOptions(
        session_url="https://jmap.example.com/.well-known/jmap",
        username="user",
        password="pass",
        transport=transport,
    )

    # Act
    with JmapClient(options) as client:
        client.connect()
        mailboxes = client.list_mailboxes("u1")

    # Assert – result shape
    assert len(mailboxes) == 1
    mb = mailboxes[0]
    assert mb.id == "mb1"
    assert mb.name == "Inbox"
    assert mb.role == "inbox"
    assert mb.total_emails == 3
    assert mb.unread_emails == 1
    assert mb.my_rights is not None
    assert mb.my_rights.may_read_items is True

    # Assert – request sent to transport
    assert transport.last_request is not None
    req = transport.last_request
    assert req.method == "POST"
    assert req.url == "https://jmap.example.com/api"
    body = json.loads(req.body)
    assert body["using"] == ["urn:ietf:params:jmap:mail"]
    invocation = body["methodCalls"][0]
    assert invocation[0] == "Mailbox/get"
    assert invocation[1]["accountId"] == "u1"


def test_list_mailboxes_empty_method_responses_raises_protocol_error() -> None:
    """Regression test: a malformed/empty server response ({"methodResponses": []}) must
    raise JmapProtocolError, not a raw IndexError - a caller catching only JmapError would
    otherwise be broken by an unrelated exception type leaking through."""
    session_resp = _make_session_response()
    empty_resp = JmapHttpResponse(
        status_code=200,
        headers={},
        body=json.dumps({"sessionState": "test", "methodResponses": []}),
    )
    transport = FakeJmapTransport(session_resp, empty_resp)

    options = JmapClientOptions(
        session_url="https://jmap.example.com/.well-known/jmap",
        username="user",
        password="pass",
        transport=transport,
    )

    with JmapClient(options) as client:
        client.connect()
        with pytest.raises(JmapProtocolError):
            client.list_mailboxes("u1")


def test_list_messages_success() -> None:
    """list_messages returns a full EmailQueryResponse and issues the correct request."""
    session_resp = _make_session_response()
    method_resp = _make_method_response(
        "Email/query",
        {
            "accountId": "u1",
            "queryState": "abc123",
            "canCalculateChanges": True,
            "position": 0,
            "ids": ["m1", "m2"],
            "total": 42,
            "limit": 10,
        },
    )
    transport = FakeJmapTransport(session_resp, method_resp)

    options = JmapClientOptions(
        session_url="https://jmap.example.com/.well-known/jmap",
        username="user",
        password="pass",
        transport=transport,
    )

    # Act
    with JmapClient(options) as client:
        client.connect()
        result = client.list_messages("u1")

    # Assert - result shape
    assert result.account_id == "u1"
    assert result.query_state == "abc123"
    assert result.can_calculate_changes is True
    assert result.position == 0
    assert result.ids == ["m1", "m2"]
    assert result.total == 42
    assert result.limit == 10

    # Assert - request sent to transport
    assert transport.last_request is not None
    req = transport.last_request
    assert req.method == "POST"
    assert req.url == "https://jmap.example.com/api"
    body = json.loads(req.body)
    assert body["using"] == ["urn:ietf:params:jmap:mail"]
    invocation = body["methodCalls"][0]
    assert invocation[0] == "Email/query"
    assert invocation[1]["accountId"] == "u1"


def test_get_mailbox_with_ids_none_returns_empty() -> None:
    """Calling get_mailbox without ids returns an empty list (no error)."""
    session_resp = _make_session_response()
    method_resp = _make_method_response(
        "Mailbox/get",
        {"accountId": "u1", "state": "1", "list": [], "notFound": []},
    )
    transport = FakeJmapTransport(session_resp, method_resp)

    options = JmapClientOptions(
        session_url="https://jmap.example.com/.well-known/jmap",
        username="user",
        password="pass",
        transport=transport,
    )

    with JmapClient(options) as client:
        client.connect()
        result = client.get_mailbox("u1")  # ids omitted

    assert result == []  # empty list expected
    # Verify that the request did not contain an "ids" key
    body = json.loads(transport.last_request.body)  # type: ignore[union-attr]
    args = body["methodCalls"][0][1]
    assert "ids" not in args


def test_protocol_error_raises() -> None:
    """A method response named \"error\" should raise JmapProtocolError."""
    session_resp = _make_session_response()
    error_resp = _make_method_response(
        "error",
        {"type": "unknownMethod", "description": "Method not found"},
    )
    transport = FakeJmapTransport(session_resp, error_resp)

    options = JmapClientOptions(
        session_url="https://jmap.example.com/.well-known/jmap",
        username="user",
        password="pass",
        transport=transport,
    )

    with JmapClient(options) as client:
        client.connect()
        with pytest.raises(JmapProtocolError) as exc_info:
            client.list_mailboxes("u1")
    assert exc_info.value.type == "unknownMethod"
    assert "Method not found" in str(exc_info.value)
