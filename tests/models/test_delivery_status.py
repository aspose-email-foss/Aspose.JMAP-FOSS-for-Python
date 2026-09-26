"""Tests for the :class:`DeliveryStatus` model.

The model is imported from the public package entry point to ensure the
re‑export works correctly."""
from __future__ import annotations

from typing import Any, Dict

import pytest

from aspose_jmap_foss import DeliveryStatus


def test_from_json_complete() -> None:
    """Deserialization populates all fields from a full JSON payload."""
    payload: Dict[str, Any] = {
        "smtpReply": "250 2.0.0 OK",
        "delivered": "yes",
        "displayed": "unknown",
    }
    status = DeliveryStatus.from_json(payload)
    assert status.smtp_reply == "250 2.0.0 OK"
    assert status.delivered == "yes"
    assert status.displayed == "unknown"


def test_to_json_matches_input() -> None:
    """Serialization yields a JSON dict identical to the original input."""
    status = DeliveryStatus(
        smtp_reply="550 5.1.1 User unknown",
        delivered="no",
        displayed="yes",
    )
    assert status.to_json() == {
        "smtpReply": "550 5.1.1 User unknown",
        "delivered": "no",
        "displayed": "yes",
    }


def test_from_json_missing_fields_default_to_empty() -> None:
    """Missing fields default to empty strings as defined by the implementation."""
    partial: Dict[str, Any] = {"smtpReply": "421 4.4.2 Timeout"}
    status = DeliveryStatus.from_json(partial)
    assert status.smtp_reply == "421 4.4.2 Timeout"
    assert status.delivered == ""
    assert status.displayed == ""


def test_from_json_null_values_preserve_none() -> None:
    """Explicit ``null`` values are preserved (not replaced by defaults)."""
    payload: Dict[str, Any] = {"smtpReply": None, "delivered": None, "displayed": None}
    status = DeliveryStatus.from_json(payload)
    assert status.smtp_reply is None
    assert status.delivered is None
    assert status.displayed is None


def test_round_trip_consistency() -> None:
    """A round‑trip through ``to_json`` and ``from_json`` preserves data."""
    original = DeliveryStatus(
        smtp_reply="250 2.0.0 OK",
        delivered="queued",
        displayed="unknown",
    )
    round_trip = DeliveryStatus.from_json(original.to_json())
    assert round_trip == original
