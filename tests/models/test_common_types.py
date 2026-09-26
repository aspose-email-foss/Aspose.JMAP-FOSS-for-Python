"""Tests for the common JMAP model types and error hierarchy.

The symbols are imported directly from the ``aspose_jmap_foss.models.common_types``
module to avoid triggering the package's top‑level ``__init__`` (which imports
other modules that are not yet present in this repository).
"""

from __future__ import annotations

from aspose_jmap_foss.models.common_types import (
    SetError,
    MethodError,
    ResultReference,
    JmapError,
    JmapProtocolError,
    JmapNetworkError,
)


def test_set_error_full_cycle() -> None:
    """Serialize and deserialize a fully populated ``SetError``."""
    original = SetError(
        type="invalidProperties",
        description="Invalid email address",
        properties=["email", "name"],
    )
    json_data = original.to_json()
    assert json_data == {
        "type": "invalidProperties",
        "description": "Invalid email address",
        "properties": ["email", "name"],
    }

    reconstructed = SetError.from_json(json_data)
    assert reconstructed == original
    assert reconstructed.description == "Invalid email address"
    assert reconstructed.properties == ["email", "name"]


def test_set_error_missing_optionals() -> None:
    """``SetError`` with only the required field should omit optional keys."""
    original = SetError(type="notFound")
    json_data = original.to_json()
    assert json_data == {"type": "notFound"}

    reconstructed = SetError.from_json(json_data)
    assert reconstructed == original
    assert reconstructed.description is None
    assert reconstructed.properties is None


def test_method_error_full_cycle() -> None:
    """Serialize and deserialize a fully populated ``MethodError``."""
    original = MethodError(type="unknownMethod", description="Method does not exist")
    json_data = original.to_json()
    assert json_data == {"type": "unknownMethod", "description": "Method does not exist"}

    reconstructed = MethodError.from_json(json_data)
    assert reconstructed == original
    assert reconstructed.description == "Method does not exist"


def test_method_error_missing_description() -> None:
    """``MethodError`` without a description should omit the key."""
    original = MethodError(type="serverFail")
    json_data = original.to_json()
    assert json_data == {"type": "serverFail"}

    reconstructed = MethodError.from_json(json_data)
    assert reconstructed == original
    assert reconstructed.description is None


def test_result_reference_full_cycle() -> None:
    """Serialize and deserialize a ``ResultReference``."""
    original = ResultReference(result_of="c1", name="created", path="/ids/0")
    json_data = original.to_json()
    assert json_data == {"resultOf": "c1", "name": "created", "path": "/ids/0"}

    reconstructed = ResultReference.from_json(json_data)
    assert reconstructed == original
    assert reconstructed.result_of == "c1"
    assert reconstructed.name == "created"
    assert reconstructed.path == "/ids/0"


def test_jmap_protocol_error_message() -> None:
    """The string representation of ``JmapProtocolError`` includes type and description."""
    exc = JmapProtocolError(type="invalidArguments", description="Bad request")
    assert isinstance(exc, JmapError)
    assert exc.type == "invalidArguments"
    assert exc.description == "Bad request"
    assert "invalidArguments" in str(exc)
    assert "Bad request" in str(exc)


def test_jmap_protocol_error_without_description() -> None:
    """When no description is supplied the message contains only the type."""
    exc = JmapProtocolError(type="accountNotFound")
    assert isinstance(exc, JmapError)
    assert exc.type == "accountNotFound"
    assert exc.description is None
    assert str(exc) == "JMAP protocol error [accountNotFound]"


def test_jmap_network_error_wrapping() -> None:
    """``JmapNetworkError`` should retain the original exception."""
    inner = ValueError("connection timed out")
    exc = JmapNetworkError(original_exception=inner)
    assert isinstance(exc, JmapError)
    assert exc.original_exception is inner
    assert "connection timed out" in str(exc)
