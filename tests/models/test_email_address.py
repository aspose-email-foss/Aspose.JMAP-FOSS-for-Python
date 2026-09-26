import pytest
from typing import Any, Dict

from aspose_jmap_foss import EmailAddress


def test_roundtrip_full_fields() -> None:
    """Serializing then deserializing preserves both fields."""
    original = EmailAddress(name="Alice", email="alice@example.com")
    json_data: Dict[str, Any] = original.to_json()
    restored = EmailAddress.from_json(json_data)

    assert restored.name == original.name
    assert restored.email == original.email


def test_to_json_includes_null_name() -> None:
    """When ``name`` is ``None`` the JSON output still contains the key with a null value."""
    addr = EmailAddress(name=None, email="bob@example.com")
    json_data = addr.to_json()
    assert json_data == {"name": None, "email": "bob@example.com"}


def test_from_json_handles_missing_name() -> None:
    """A missing ``name`` field in the input JSON results in ``name`` being ``None``."""
    payload = {"email": "carol@example.com"}
    addr = EmailAddress.from_json(payload)
    assert addr.name is None
    assert addr.email == "carol@example.com"


def test_from_json_explicit_null_name() -> None:
    """An explicit ``null`` for ``name`` is treated the same as a missing field."""
    payload = {"name": None, "email": "dave@example.com"}
    addr = EmailAddress.from_json(payload)
    assert addr.name is None
    assert addr.email == "dave@example.com"


def test_from_json_missing_email_raises_key_error() -> None:
    """The required ``email`` property must be present; otherwise a ``KeyError`` is raised."""
    payload = {"name": "Eve"}
    with pytest.raises(KeyError):
        EmailAddress.from_json(payload)
