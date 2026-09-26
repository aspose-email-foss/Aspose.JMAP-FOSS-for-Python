"""Tests for the public EmailHeader model."""

from __future__ import annotations

import pytest

from aspose_jmap_foss import EmailHeader


def test_from_json_creates_instance() -> None:
    """Normal case: from_json returns a correctly populated EmailHeader."""
    payload = {"name": "Subject", "value": "Hello, world!"}
    header = EmailHeader.from_json(payload)

    assert isinstance(header, EmailHeader)
    assert header.name == "Subject"
    assert header.value == "Hello, world!"


def test_to_json_round_trip() -> None:
    """Normal case: to_json reproduces the original JSON payload."""
    payload = {"name": "X-Custom-Header", "value": "12345"}
    header = EmailHeader.from_json(payload)
    assert header.to_json() == payload


def test_empty_strings_allowed() -> None:
    """Edge case: header fields may be empty strings without error."""
    payload = {"name": "", "value": ""}
    header = EmailHeader.from_json(payload)
    assert header.name == ""
    assert header.value == ""
    assert header.to_json() == payload


def test_missing_field_raises_key_error() -> None:
    """Edge case: omitting a required field should raise KeyError."""
    incomplete_payload = {"name": "From"}  # 'value' is missing
    with pytest.raises(KeyError) as exc_info:
        EmailHeader.from_json(incomplete_payload)
    assert exc_info.value.args[0] == "value"
