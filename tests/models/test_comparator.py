"""Tests for the public :class:`Comparator` model."""

from __future__ import annotations

import sys
import types
from typing import Any

# ----------------------------------------------------------------------
# Stub the parts of the package that are not generated yet but are
# imported by ``aspose_jmap_foss.__init__``.  Only the symbols required for
# the import to succeed are provided; they are never used by the tests.
# ----------------------------------------------------------------------
# aspose_jmap_foss.common_types
common_types_mod = types.ModuleType("aspose_jmap_foss.common_types")
for name in ("JmapError", "JmapNetworkError", "JmapProtocolError"):
    setattr(common_types_mod, name, type(name, (Exception,), {}))
sys.modules["aspose_jmap_foss.common_types"] = common_types_mod

# aspose_jmap_foss.transport (used by client_core)
transport_mod = types.ModuleType("aspose_jmap_foss.transport")
class JmapTransport:  # pragma: no cover
    """Placeholder transport ABC."""
    pass
transport_mod.JmapTransport = JmapTransport
sys.modules["aspose_jmap_foss.transport"] = transport_mod

# aspose_jmap_foss.request (used by client_core)
request_mod = types.ModuleType("aspose_jmap_foss.request")
class JmapHttpRequest:  # pragma: no cover
    """Placeholder request class."""
    pass
request_mod.JmapHttpRequest = JmapHttpRequest
sys.modules["aspose_jmap_foss.request"] = request_mod

# aspose_jmap_foss.response (used by client_core)
response_mod = types.ModuleType("aspose_jmap_foss.response")
class JmapHttpResponse:  # pragma: no cover
    """Placeholder response class."""
    pass
response_mod.JmapHttpResponse = JmapHttpResponse
sys.modules["aspose_jmap_foss.response"] = response_mod

# aspose_jmap_foss.client_mail and client_submission – empty stubs
sys.modules["aspose_jmap_foss.client_mail"] = types.ModuleType("aspose_jmap_foss.client_mail")
sys.modules["aspose_jmap_foss.client_submission"] = types.ModuleType(
    "aspose_jmap_foss.client_submission"
)

# Now the public package can be imported safely.
from aspose_jmap_foss import Comparator


def test_from_json_all_fields() -> None:
    """Deserialization when every field is present."""
    data: dict[str, Any] = {
        "property": "subject",
        "isAscending": False,
        "collation": "en-US",
    }
    comp = Comparator.from_json(data)

    assert comp.property == "subject"
    assert comp.is_ascending is False
    assert comp.collation == "en-US"


def test_from_json_missing_optional_fields() -> None:
    """Deserialization uses defaults when optional fields are omitted."""
    data: dict[str, Any] = {
        "property": "receivedAt",
        # isAscending omitted → defaults to True
        # collation omitted → defaults to None
    }
    comp = Comparator.from_json(data)

    assert comp.property == "receivedAt"
    assert comp.is_ascending is True
    assert comp.collation is None


def test_to_json_includes_all_set_fields() -> None:
    """Serialization includes all non‑None fields."""
    comp = Comparator(property="size", is_ascending=False, collation="fr-FR")
    json_dict = comp.to_json()

    expected = {
        "property": "size",
        "isAscending": False,
        "collation": "fr-FR",
    }
    assert json_dict == expected


def test_to_json_omits_none_collation() -> None:
    """Serialization omits the ``collation`` key when its value is ``None``."""
    comp = Comparator(property="from", is_ascending=True, collation=None)
    json_dict = comp.to_json()

    expected = {
        "property": "from",
        "isAscending": True,
    }
    assert json_dict == expected


def test_round_trip_serialization() -> None:
    """A round‑trip through ``from_json`` → ``to_json`` preserves data."""
    original: dict[str, Any] = {
        "property": "subject",
        "isAscending": True,
        # collation omitted → None
    }
    comp = Comparator.from_json(original)
    round_trip = comp.to_json()
    assert round_trip == original
