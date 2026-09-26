"""Tests for the Email and EmailBodyValue model classes."""

from __future__ import annotations

import copy
from typing import Any, Dict, List

import pytest

from aspose_jmap_foss import Email, EmailBodyValue, EmailAddress, EmailBodyPart


def _make_address(email: str, name: str | None = None) -> Dict[str, Any]:
    """Factory for an address JSON object."""
    return {"email": email, "name": name}


def _make_body_part(size: int, type_: str, headers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Factory for a minimal EmailBodyPart JSON object."""
    # Include all optional fields explicitly set to None so that round‑trip
    # serialization matches the model's `to_json` output.
    return {
        "size": size,
        "type": type_,
        "headers": headers,
        "partId": None,
        "blobId": None,
        "name": None,
        "charset": None,
        "disposition": None,
        "cid": None,
        "language": None,
        "location": None,
        "subParts": None,
    }


def test_email_body_value_roundtrip() -> None:
    """Serialize and deserialize an EmailBodyValue."""
    json_data: Dict[str, Any] = {
        "value": "Hello, world!",
        "isEncodingProblem": False,
        "isTruncated": True,
    }
    body_value = EmailBodyValue.from_json(json_data)
    assert isinstance(body_value, EmailBodyValue)
    assert body_value.value == "Hello, world!"
    assert body_value.is_encoding_problem is False
    assert body_value.is_truncated is True
    assert body_value.to_json() == json_data


def test_email_full_roundtrip() -> None:
    """Deserialize a fully populated Email and serialize back to equivalent JSON."""
    json_data: Dict[str, Any] = {
        "id": "email123",
        "blobId": "blob456",
        "threadId": "thread789",
        "mailboxIds": {"mailbox1": True, "mailbox2": False},
        "keywords": {"$seen": True},
        "size": 1024,
        "receivedAt": "2023-01-01T12:00:00Z",
        "messageId": ["<msgid@example.com>"],
        "inReplyTo": ["<prev@example.com>"],
        "references": ["<ref1@example.com>", "<ref2@example.com>"],
        "sender": [_make_address("alice@example.com", "Alice")],
        "from": [_make_address("bob@example.com", "Bob")],
        "to": [_make_address("carol@example.com")],
        "cc": [_make_address("dave@example.com")],
        "bcc": [_make_address("eve@example.com")],
        "replyTo": [_make_address("frank@example.com")],
        "subject": "Test",
        "sentAt": "2023-01-01T11:00:00Z",
        "bodyStructure": _make_body_part(200, "text/plain", []),
        "bodyValues": {
            "textBody": {
                "value": "Hello",
                "isEncodingProblem": False,
                "isTruncated": False,
            }
        },
        "textBody": [_make_body_part(200, "text/plain", [])],
        "htmlBody": [_make_body_part(300, "text/html", [])],
        "attachments": [_make_body_part(400, "application/pdf", [])],
        "hasAttachment": True,
        "preview": "Preview text",
    }

    email = Email.from_json(json_data)

    # Spot‑check a representative subset of fields.
    assert email.id == "email123"
    assert email.blob_id == "blob456"
    assert email.thread_id == "thread789"
    assert email.mailbox_ids == {"mailbox1": True, "mailbox2": False}
    assert email.keywords == {"$seen": True}
    assert email.size == 1024
    assert email.received_at == "2023-01-01T12:00:00Z"
    assert email.message_id == ["<msgid@example.com>"]
    assert email.sender is not None and email.sender[0].email == "alice@example.com"
    assert email.from_ is not None and email.from_[0].name == "Bob"
    assert email.to is not None and email.to[0].email == "carol@example.com"
    assert email.body_structure is not None
    # Verify a field of the nested EmailBodyPart.
    assert email.body_structure.type == "text/plain"
    assert "textBody" in email.body_values
    assert email.body_values["textBody"].value == "Hello"
    assert email.has_attachment is True
    assert email.preview == "Preview text"

    # Build the expected JSON that includes the explicit None fields emitted by `to_json`.
    expected_json = copy.deepcopy(json_data)
    # The model's `to_json` always includes the optional keys with value None.
    for key in ("bodyStructure", "textBody", "htmlBody", "attachments"):
        if isinstance(expected_json.get(key), dict):
            # single body part
            part = expected_json[key]
            for opt in (
                "partId",
                "blobId",
                "name",
                "charset",
                "disposition",
                "cid",
                "language",
                "location",
                "subParts",
            ):
                part.setdefault(opt, None)
        elif isinstance(expected_json.get(key), list):
            for part in expected_json[key]:
                for opt in (
                    "partId",
                    "blobId",
                    "name",
                    "charset",
                    "disposition",
                    "cid",
                    "language",
                    "location",
                    "subParts",
                ):
                    part.setdefault(opt, None)

    assert email.to_json() == expected_json


def test_email_minimal_required_fields() -> None:
    """An Email containing only the required mailboxIds field."""
    json_data: Dict[str, Any] = {
        "mailboxIds": {"inbox": True},
    }

    email = Email.from_json(json_data)

    # Required mutable metadata must be present.
    assert email.mailbox_ids == {"inbox": True}
    # All optional fields should be their defaults / None.
    assert email.id is None
    assert email.keywords == {}
    assert email.sender is None
    assert email.body_structure is None
    assert email.body_values == {}
    assert email.text_body == []
    assert email.html_body == []
    assert email.attachments == []

    # Serialisation should emit only the required field.
    assert email.to_json() == {"mailboxIds": {"inbox": True}}


def test_email_null_optional_fields_omitted_in_json() -> None:
    """Fields set to None should be omitted from the serialized JSON."""
    email = Email(
        mailbox_ids={"inbox": True},
        # Explicitly set optional fields to None
        id=None,
        blob_id=None,
        thread_id=None,
        keywords={},
        size=None,
        received_at=None,
        message_id=None,
        in_reply_to=None,
        references=None,
        sender=None,
        from_=None,
        to=None,
        cc=None,
        bcc=None,
        reply_to=None,
        subject=None,
        sent_at=None,
        body_structure=None,
        body_values={},
        text_body=[],
        html_body=[],
        attachments=[],
        has_attachment=None,
        preview=None,
    )
    # Only mailboxIds should appear.
    assert email.to_json() == {"mailboxIds": {"inbox": True}}
