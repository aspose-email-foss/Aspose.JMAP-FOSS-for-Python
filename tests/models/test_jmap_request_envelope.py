"""Tests for :class:`aspose_jmap_foss.JmapRequestEnvelope`."""

from __future__ import annotations

import json
from typing import Any, List, Dict

import pytest

# Public import as required by the style guide.
from aspose_jmap_foss import JmapRequestEnvelope


class _InvocationStub:
    """A tiny stand‑in for :class:`aspose_jmap_foss.models.invocation.Invocation`.

    It provides the attributes and ``to_json`` method needed for the envelope
    serialization tests without pulling in the real implementation.
    """

    def __init__(self, name: str, arguments: Dict[str, Any], method_call_id: str) -> None:
        self.name = name
        self.arguments = arguments
        self.method_call_id = method_call_id

    def to_json(self) -> List[Any]:
        return [self.name, self.arguments, self.method_call_id]


def test_from_json_full() -> None:
    """Deserialize a complete envelope, including a populated ``createdIds``."""
    payload = {
        "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
        "methodCalls": [
            ["Email/get", {"accountId": "user-123", "ids": ["m1"]}, "c1"],
            ["Mailbox/get", {"accountId": "user-123"}, "c2"],
        ],
        "createdIds": {"client-1": "server-1", "client-2": "server-2"},
    }

    envelope = JmapRequestEnvelope.from_json(payload)

    assert envelope.using == payload["using"]
    assert envelope.created_ids == payload["createdIds"]
    assert len(envelope.method_calls) == 2

    for inv_obj, inv_json in zip(envelope.method_calls, payload["methodCalls"]):
        # The real Invocation class is not imported directly; we rely on duck typing.
        assert hasattr(inv_obj, "name")
        assert hasattr(inv_obj, "arguments")
        assert hasattr(inv_obj, "method_call_id")
        assert inv_obj.name == inv_json[0]
        assert inv_obj.arguments == inv_json[1]
        assert inv_obj.method_call_id == inv_json[2]


def test_from_json_without_created_ids() -> None:
    """Deserialize when ``createdIds`` is omitted – it should become ``None``."""
    payload = {
        "using": ["urn:ietf:params:jmap:core"],
        "methodCalls": [
            ["Identity/get", {"accountId": "user-123"}, "c3"],
        ],
        # ``createdIds`` key is intentionally absent.
    }

    envelope = JmapRequestEnvelope.from_json(payload)

    assert envelope.using == payload["using"]
    assert envelope.created_ids is None
    assert len(envelope.method_calls) == 1
    inv = envelope.method_calls[0]
    assert inv.name == "Identity/get"
    assert inv.arguments == {"accountId": "user-123"}
    assert inv.method_call_id == "c3"


def test_to_json_round_trip() -> None:
    """Serialize an envelope and ensure the output matches the expected wire format."""
    stub_inv = _InvocationStub(
        name="Email/set",
        arguments={"accountId": "user-123", "create": {}},
        method_call_id="c4",
    )
    envelope = JmapRequestEnvelope(
        using=["urn:ietf:params:jmap:core"],
        method_calls=[stub_inv],
        created_ids=None,
    )

    json_dict = envelope.to_json()
    expected = {
        "using": ["urn:ietf:params:jmap:core"],
        "methodCalls": [
            ["Email/set", {"accountId": "user-123", "create": {}}, "c4"]
        ],
        "createdIds": None,
    }
    assert json_dict == expected

    # Verify JSON round‑trip works.
    round_trip = json.loads(json.dumps(json_dict))
    assert round_trip == expected


def test_camel_case_aliases() -> None:
    """The camelCase property aliases should stay in sync with their snake_case counterparts."""
    envelope = JmapRequestEnvelope(using=["urn:ietf:params:jmap:core"])
    # Set via camelCase alias
    envelope.methodCalls = [_InvocationStub("Foo/get", {}, "id1")]
    envelope.createdIds = {"c1": "s1"}

    # Verify snake_case attributes reflect the changes
    assert len(envelope.method_calls) == 1
    assert envelope.method_calls[0].name == "Foo/get"
    assert envelope.created_ids == {"c1": "s1"}

    # Mutate snake_case and check camelCase view
    envelope.method_calls.append(_InvocationStub("Bar/get", {}, "id2"))
    envelope.created_ids = None
    assert envelope.methodCalls[-1].name == "Bar/get"
    assert envelope.createdIds is None
