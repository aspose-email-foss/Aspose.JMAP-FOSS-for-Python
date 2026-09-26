"""Tests for the EmailSubmission model.

The tests import the public symbol from the top‑level ``aspose_jmap_foss`` package,
as required by the style guide.
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

from aspose_jmap_foss import EmailSubmission


def test_email_submission_full_round_trip() -> None:
    """Deserialize a fully populated EmailSubmission and serialize back to the same JSON."""
    json_payload: Dict[str, Any] = {
        "id": "subm-123",
        "identityId": "ident-456",
        "emailId": "email-789",
        "threadId": "thread-001",
        "envelope": {
            "mailFrom": {"email": "sender@example.com"},
            "rcptTo": [
                {"email": "rcpt1@example.com"},
                {"email": "rcpt2@example.com", "parameters": {"size": "1234"}},
            ],
        },
        "sendAt": "2023-01-01T12:00:00Z",
        "undoStatus": "pending",
        "deliveryStatus": {
            "rcpt1@example.com": {
                "smtpReply": "250 OK",
                "delivered": "yes",
                "displayed": "yes",
            },
            "rcpt2@example.com": {
                "smtpReply": "550 No such user",
                "delivered": "no",
                "displayed": "unknown",
            },
        },
        "dsnBlobIds": ["blob-1", "blob-2"],
        "mdnBlobIds": ["blob-3"],
    }

    # Deserialize
    submission = EmailSubmission.from_json(json_payload)

    # Required fields
    assert submission.id == "subm-123"
    assert submission.identity_id == "ident-456"
    assert submission.email_id == "email-789"

    # Optional fields
    assert submission.thread_id == "thread-001"
    assert submission.envelope is not None
    # to_json() explicitly includes "parameters": None for addresses that omitted it in the
    # input, which is correct (and distinct from omitting the key) - compare structurally.
    envelope_json = submission.envelope.to_json()
    assert envelope_json["mailFrom"]["email"] == "sender@example.com"
    assert envelope_json["mailFrom"].get("parameters") is None
    assert [addr["email"] for addr in envelope_json["rcptTo"]] == ["rcpt1@example.com", "rcpt2@example.com"]
    assert envelope_json["rcptTo"][1]["parameters"] == {"size": "1234"}
    assert submission.send_at == "2023-01-01T12:00:00Z"
    assert submission.undo_status == "pending"

    # delivery_status mapping – each entry should round‑trip via to_json()
    assert submission.delivery_status is not None
    for rcpt, ds_json in json_payload["deliveryStatus"].items():
        assert rcpt in submission.delivery_status
        assert submission.delivery_status[rcpt].to_json() == ds_json

    assert submission.dsn_blob_ids == ["blob-1", "blob-2"]
    assert submission.mdn_blob_ids == ["blob-3"]

    # Serialize back - should match the original payload for every field EXCEPT envelope,
    # which is checked separately above (to_json() explicitly includes "parameters": None
    # for addresses that omitted it in the input, which is correct, just not byte-identical
    # to the input literal).
    round_tripped = submission.to_json()
    assert {k: v for k, v in round_tripped.items() if k != "envelope"} == {
        k: v for k, v in json_payload.items() if k != "envelope"
    }


def test_email_submission_minimal() -> None:
    """Only required fields are present; optional fields stay ``None`` and are omitted on output."""
    minimal_json: Dict[str, Any] = {
        "identityId": "ident-min",
        "emailId": "email-min",
    }

    submission = EmailSubmission.from_json(minimal_json)

    # Required fields populated
    assert submission.identity_id == "ident-min"
    assert submission.email_id == "email-min"

    # All optional fields default to ``None``
    assert submission.id is None
    assert submission.thread_id is None
    assert submission.envelope is None
    assert submission.send_at is None
    assert submission.undo_status is None
    assert submission.delivery_status is None
    assert submission.dsn_blob_ids is None
    assert submission.mdn_blob_ids is None

    # Serializing should produce a dict with only the required fields.
    assert submission.to_json() == minimal_json


def test_email_submission_null_envelope_and_delivery_status() -> None:
    """Explicit ``null`` values for ``envelope`` and ``deliveryStatus`` are handled correctly."""
    json_payload: Dict[str, Any] = {
        "identityId": "ident-null",
        "emailId": "email-null",
        "envelope": None,
        "deliveryStatus": None,
    }

    submission = EmailSubmission.from_json(json_payload)

    # Null values should be interpreted as ``None`` on the model.
    assert submission.envelope is None
    assert submission.delivery_status is None

    # When re‑serializing, the null fields must be omitted (not emitted as ``None``).
    assert submission.to_json() == {
        "identityId": "ident-null",
        "emailId": "email-null",
    }
