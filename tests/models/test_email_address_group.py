"""Tests for the EmailAddressGroup model."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from aspose_jmap_foss import EmailAddressGroup, EmailAddress


def test_from_json_full() -> None:
    """Deserialize a full JSON payload and verify fields."""
    data: Dict[str, Any] = {
        "name": "Team",
        "addresses": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": None, "email": "bob@example.com"},
        ],
    }
    group = EmailAddressGroup.from_json(data)

    assert group.name == "Team"
    assert len(group.addresses) == 2

    # Verify first address
    addr0 = group.addresses[0]
    assert getattr(addr0, "email") == "alice@example.com"
    assert getattr(addr0, "name") == "Alice"

    # Verify second address (null name)
    addr1 = group.addresses[1]
    assert getattr(addr1, "email") == "bob@example.com"
    assert getattr(addr1, "name") is None


def test_to_json_full() -> None:
    """Serialize a fully populated EmailAddressGroup and compare JSON."""
    group = EmailAddressGroup(
        name="Team",
        addresses=[
            EmailAddress(name="Alice", email="alice@example.com"),
            EmailAddress(name=None, email="bob@example.com"),
        ],
    )
    expected: Dict[str, Any] = {
        "name": "Team",
        "addresses": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": None, "email": "bob@example.com"},
        ],
    }
    assert group.to_json() == expected


def test_from_json_missing_name_and_empty_addresses() -> None:
    """When optional fields are omitted, defaults are applied correctly."""
    data: Dict[str, Any] = {"addresses": []}
    group = EmailAddressGroup.from_json(data)

    assert group.name is None
    assert group.addresses == []


def test_round_trip_with_null_name() -> None:
    """Serializing then deserializing preserves data, even with a null name."""
    original = EmailAddressGroup(
        name=None,
        addresses=[EmailAddress(name="Charlie", email="charlie@example.com")],
    )
    json_repr = original.to_json()
    restored = EmailAddressGroup.from_json(json_repr)

    assert restored.name is None
    assert len(restored.addresses) == 1
    restored_addr = restored.addresses[0]
    assert getattr(restored_addr, "name") == "Charlie"
    assert getattr(restored_addr, "email") == "charlie@example.com"
