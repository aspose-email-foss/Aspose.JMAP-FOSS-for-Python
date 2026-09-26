"""Tests for the public :class:`Identity` model."""

from __future__ import annotations

import pytest

from aspose_jmap_foss import Identity


def test_identity_full_round_trip() -> None:
    """Serialize and deserialize a fully populated Identity payload."""
    json_payload = {
        "id": "id123",
        "name": "John Doe",
        "email": "john@example.com",
        "replyTo": [
            {"name": "Reply One", "email": "reply1@example.com"},
            {"name": None, "email": "reply2@example.com"},
        ],
        "bcc": [
            {"name": "Bcc One", "email": "bcc1@example.com"},
        ],
        "textSignature": "Best regards",
        "htmlSignature": "<p>Best regards</p>",
        "mayDelete": True,
    }

    identity = Identity.from_json(json_payload)

    # Verify fields are populated as expected.
    assert identity.id == "id123"
    assert identity.name == "John Doe"
    assert identity.email == "john@example.com"

    assert isinstance(identity.reply_to, list) and len(identity.reply_to) == 2
    assert identity.reply_to[0].name == "Reply One"
    assert identity.reply_to[0].email == "reply1@example.com"
    assert identity.reply_to[1].name is None
    assert identity.reply_to[1].email == "reply2@example.com"

    assert isinstance(identity.bcc, list) and len(identity.bcc) == 1
    assert identity.bcc[0].name == "Bcc One"
    assert identity.bcc[0].email == "bcc1@example.com"

    assert identity.text_signature == "Best regards"
    assert identity.html_signature == "<p>Best regards</p>"
    assert identity.may_delete is True

    # Round‑trip should reproduce the original JSON (order of keys is irrelevant).
    assert identity.to_json() == json_payload


def test_identity_partial_and_null_fields() -> None:
    """Handle missing optional fields and explicit nulls, ensuring correct defaults and omission."""
    json_payload = {
        "email": "alice@example.com",
        "replyTo": None,  # explicit null should be treated as absent
        "mayDelete": None,
    }

    identity = Identity.from_json(json_payload)

    # Required field.
    assert identity.email == "alice@example.com"

    # Optional fields should have defaults or be None.
    assert identity.id is None
    assert identity.name == ""
    assert identity.reply_to is None
    assert identity.bcc is None
    assert identity.text_signature == ""
    assert identity.html_signature == ""
    assert identity.may_delete is None

    # to_json must omit keys whose values are None.
    expected_output = {
        "email": "alice@example.com",
        "name": "",
        "textSignature": "",
        "htmlSignature": "",
    }
    assert identity.to_json() == expected_output
