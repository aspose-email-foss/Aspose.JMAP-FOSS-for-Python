"""Tests for the public ``SearchSnippet`` model."""

from __future__ import annotations

import sys
import types

# --------------------------------------------------------------------------- #
# Stub out missing submodules that the package's ``__init__`` imports.
# This allows importing ``aspose_jmap_foss`` without pulling in the full
# implementation (which is outside the scope of this isolated test).
# --------------------------------------------------------------------------- #

_missing_modules = [
    "aspose_jmap_foss.models.invocation",
    "aspose_jmap_foss.models.comparator",
    "aspose_jmap_foss.models.delivery_status",
    "aspose_jmap_foss.models.email_address",
    "aspose_jmap_foss.models.email_address_group",
    "aspose_jmap_foss.models.email_body_part",
    "aspose_jmap_foss.models.email_header",
    "aspose_jmap_foss.common_types",
]
for _mod_name in _missing_modules:
    sys.modules.setdefault(_mod_name, types.ModuleType(_mod_name))

# Provide minimal placeholder symbols required by ``client_core``.
# The real library defines proper exception hierarchies; for the purpose of
# this test they only need to exist.
_common = sys.modules["aspose_jmap_foss.common_types"]
_common.JmapError = type("JmapError", (Exception,), {})
_common.JmapNetworkError = type("JmapNetworkError", (Exception,), {})
_common.JmapProtocolError = type("JmapProtocolError", (Exception,), {})

# --------------------------------------------------------------------------- #
# Import the class under test via the public package entry point.
# --------------------------------------------------------------------------- #
from aspose_jmap_foss import SearchSnippet


def test_search_snippet_full_cycle() -> None:
    """Serialize a fully‑populated instance to JSON and back."""
    snippet = SearchSnippet(
        email_id="email123",
        subject="<mark>Hello</mark> World",
        preview="This is a <mark>preview</mark> snippet.",
    )
    json_data = snippet.to_json()
    assert json_data == {
        "emailId": "email123",
        "subject": "<mark>Hello</mark> World",
        "preview": "This is a <mark>preview</mark> snippet.",
    }

    reconstructed = SearchSnippet.from_json(json_data)
    assert reconstructed == snippet


def test_search_snippet_optional_fields() -> None:
    """Deserialization works when optional fields are omitted or explicitly null."""
    # Omitted optional fields – ``subject`` and ``preview`` default to ``None``.
    json_omitted = {"emailId": "email456"}
    snippet_omitted = SearchSnippet.from_json(json_omitted)
    assert snippet_omitted.email_id == "email456"
    assert snippet_omitted.subject is None
    assert snippet_omitted.preview is None
    # ``to_json`` must still emit the keys with ``None`` values.
    assert snippet_omitted.to_json() == {
        "emailId": "email456",
        "subject": None,
        "preview": None,
    }

    # Explicit ``null`` values in the payload.
    json_nulls = {"emailId": "email789", "subject": None, "preview": None}
    snippet_nulls = SearchSnippet.from_json(json_nulls)
    assert snippet_nulls.email_id == "email789"
    assert snippet_nulls.subject is None
    assert snippet_nulls.preview is None
    assert snippet_nulls.to_json() == json_nulls
