"""Tests for Session, Account, and CoreCapability model (de)serialization.

The public package ``aspose_jmap_foss`` re‑exports the model classes, so we import
them directly from the top‑level package.
"""

from __future__ import annotations

import pytest

from aspose_jmap_foss import Session, Account, CoreCapability


@pytest.fixture
def core_capability_json() -> dict:
    """Complete JSON representation of a CoreCapability object."""
    return {
        "maxSizeUpload": 50_000_000,
        "maxConcurrentUpload": 4,
        "maxSizeRequest": 10_000_000,
        "maxConcurrentRequests": 8,
        "maxCallsInRequest": 16,
        "maxObjectsInGet": 500,
        "maxObjectsInSet": 250,
        "collationAlgorithms": ["i;unicode-casemap"],
    }


def test_core_capability_roundtrip(core_capability_json: dict) -> None:
    """CoreCapability.from_json / to_json should be lossless."""
    cap = CoreCapability.from_json(core_capability_json)
    assert isinstance(cap, CoreCapability)
    assert cap.to_json() == core_capability_json


def test_core_capability_missing_required_field() -> None:
    """Missing a required field should raise a KeyError."""
    incomplete = {"maxSizeUpload": 1}
    with pytest.raises(KeyError):
        CoreCapability.from_json(incomplete)


def test_account_full_serialization() -> None:
    """Account with all optional fields should round‑trip correctly."""
    json_data = {
        "name": "Alice",
        "isPersonal": True,
        "isReadOnly": False,
        "accountCapabilities": {"urn:ietf:params:jmap:mail": {}},
    }
    acc = Account.from_json(json_data)
    assert acc.name == "Alice"
    assert acc.is_personal is True
    assert acc.is_read_only is False
    assert acc.account_capabilities == {"urn:ietf:params:jmap:mail": {}}
    assert acc.to_json() == json_data


def test_account_partial_serialization() -> None:
    """Account with missing optional fields should omit them in to_json."""
    acc = Account.from_json({})
    assert acc.name is None
    assert acc.is_personal is None
    assert acc.is_read_only is None
    assert acc.account_capabilities == {}
    assert acc.to_json() == {}


@pytest.fixture
def session_json(core_capability_json: dict) -> dict:
    """A complete Session payload containing required fields and nested objects."""
    return {
        "capabilities": {
            "urn:ietf:params:jmap:core": core_capability_json,
            "urn:ietf:params:jmap:mail": {},  # placeholder for another capability
        },
        "accounts": {
            "acc1": {
                "name": "User One",
                "isPersonal": True,
                "isReadOnly": False,
                "accountCapabilities": {"urn:ietf:params:jmap:mail": {}},
            },
            "acc2": {},  # minimal account, all optional fields omitted
        },
        "primaryAccounts": {
            "urn:ietf:params:jmap:mail": "acc1",
        },
        "username": "user@example.com",
        "apiUrl": "https://example.com/jmap",
        "downloadUrl": "https://example.com/download/{accountId}/{blobId}/{type}/{name}",
        "uploadUrl": "https://example.com/upload/{accountId}",
        "eventSourceUrl": "https://jmap.example.test/eventsource/",
        "state": "s1",
        "eventSourceUrl": "https://example.com/eventsource/{accountId}",
        "state": "someState",
    }


def test_session_roundtrip(session_json: dict) -> None:
    """Session.from_json / to_json should be lossless for a full payload."""
    sess = Session.from_json(session_json)

    # Verify scalar fields.
    assert sess.username == "user@example.com"
    assert sess.api_url == "https://example.com/jmap"
    assert sess.download_url == "https://example.com/download/{accountId}/{blobId}/{type}/{name}"
    assert sess.upload_url == "https://example.com/upload/{accountId}"
    assert sess.event_source_url == "https://example.com/eventsource/{accountId}"
    assert sess.state == "someState"

    # Capabilities are kept as raw dicts; no automatic conversion to model objects.
    assert sess.capabilities["urn:ietf:params:jmap:core"] == session_json["capabilities"]["urn:ietf:params:jmap:core"]
    assert sess.capabilities["urn:ietf:params:jmap:mail"] == {}

    # Verify accounts mapping and nested Account objects.
    acc1 = sess.accounts["acc1"]
    assert isinstance(acc1, Account)
    assert acc1.name == "User One"
    assert acc1.is_personal is True
    assert acc1.is_read_only is False
    assert acc1.account_capabilities == {"urn:ietf:params:jmap:mail": {}}

    acc2 = sess.accounts["acc2"]
    assert isinstance(acc2, Account)
    assert acc2.name is None
    assert acc2.account_capabilities == {}

    # Verify primary accounts mapping.
    assert sess.primary_accounts == {"urn:ietf:params:jmap:mail": "acc1"}

    # Serializing back must reproduce the original JSON exactly.
    assert sess.to_json() == session_json
