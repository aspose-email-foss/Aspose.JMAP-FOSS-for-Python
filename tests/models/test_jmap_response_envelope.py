"""Tests for :class:`aspose_jmap_foss.JmapResponseEnvelope` (de)serialization."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

# Public re‑exports from the package root.
from aspose_jmap_foss import JmapResponseEnvelope, Invocation


def _make_invocation() -> List[Any]:
    """Return a valid wire‑format Invocation array."""
    return [
        "Email/get",
        {"accountId": "user-123", "ids": ["msg-1"]},
        "call-1",
    ]


def test_roundtrip_full_envelope() -> None:
    """Serialize and deserialize a full envelope including optional ``createdIds``."""
    invocation = _make_invocation()
    envelope_json: Dict[str, Any] = {
        "methodResponses": [invocation],
        "createdIds": {"msg-1": "new-id-1"},
        "sessionState": "sess-42",
    }

    envelope = JmapResponseEnvelope.from_json(envelope_json)

    # Verify the inner Invocation instance.
    assert isinstance(envelope.method_responses, list)
    assert len(envelope.method_responses) == 1
    inv = envelope.method_responses[0]
    assert isinstance(inv, Invocation)
    assert inv.name == "Email/get"
    assert inv.arguments == {"accountId": "user-123", "ids": ["msg-1"]}
    assert inv.method_call_id == "call-1"

    # Verify envelope fields.
    assert envelope.created_ids == {"msg-1": "new-id-1"}
    assert envelope.session_state == "sess-42"

    # Serializing must reproduce the original JSON exactly.
    assert envelope.to_json() == envelope_json


def test_envelope_without_created_ids() -> None:
    """Deserialize an envelope where ``createdIds`` is omitted and ensure it round‑trips."""
    invocation = _make_invocation()
    minimal_json: Dict[str, Any] = {
        "methodResponses": [invocation],
        "sessionState": "sess-99",
    }

    envelope = JmapResponseEnvelope.from_json(minimal_json)

    # ``created_ids`` should be ``None`` when the key is missing.
    assert envelope.created_ids is None
    assert envelope.session_state == "sess-99"

    # Serializing must omit the ``createdIds`` key entirely.
    assert envelope.to_json() == minimal_json


def test_envelope_created_ids_null() -> None:
    """Handle a ``createdIds`` field explicitly set to ``null``."""
    invocation = _make_invocation()
    json_with_null: Dict[str, Any] = {
        "methodResponses": [invocation],
        "createdIds": None,
        "sessionState": "sess-null",
    }

    envelope = JmapResponseEnvelope.from_json(json_with_null)

    assert envelope.created_ids is None
    assert envelope.session_state == "sess-null"

    # The null should be omitted on serialization (implementation adds the key only if not None).
    expected_serialized: Dict[str, Any] = {
        "methodResponses": [invocation],
        "sessionState": "sess-null",
    }
    assert envelope.to_json() == expected_serialized


def test_envelope_with_error_invocation() -> None:
    """Ensure that an ``error`` invocation round‑trips like any other invocation."""
    error_invocation: List[Any] = [
        "error",
        {"type": "invalidArguments", "description": "Bad arguments"},
        "err-call-1",
    ]
    envelope_json: Dict[str, Any] = {
        "methodResponses": [error_invocation],
        "sessionState": "sess-err",
    }

    envelope = JmapResponseEnvelope.from_json(envelope_json)

    assert len(envelope.method_responses) == 1
    inv = envelope.method_responses[0]
    assert inv.name == "error"
    assert inv.arguments == {"type": "invalidArguments", "description": "Bad arguments"}
    assert inv.method_call_id == "err-call-1"

    # Serializing must preserve the error invocation unchanged.
    assert envelope.to_json() == envelope_json
