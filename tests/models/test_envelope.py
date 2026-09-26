"""Tests for the Envelope and Address model classes.

The public package `aspose_jmap_foss` imports many modules that are not yet
generated in this kata.  To keep the test suite importable we create minimal
stub modules for the missing symbols before importing the public symbols under
test.
"""

from __future__ import annotations

import sys
import types
from typing import Any, Dict, List

# ----------------------------------------------------------------------
# Stub missing top‑level and model submodules so that `import aspose_jmap_foss`
# succeeds without pulling in the real implementations (which are not part of
# this task).
# ----------------------------------------------------------------------
_stub_modules: dict[str, List[str]] = {
    # Core error types expected by client_core.
    "aspose_jmap_foss.common_types": [
        "JmapError",
        "JmapNetworkError",
        "JmapProtocolError",
    ],
    # Model submodules referenced by the package's __init__ (and other tests).
    "aspose_jmap_foss.models.invocation": ["Invocation"],
    "aspose_jmap_foss.models.comparator": ["Comparator"],
    "aspose_jmap_foss.models.delivery_status": ["DeliveryStatus"],
    "aspose_jmap_foss.models.email_address": ["EmailAddress"],
    "aspose_jmap_foss.models.email_address_group": ["EmailAddressGroup"],
    "aspose_jmap_foss.models.email_body_part": ["EmailBodyPart"],
    "aspose_jmap_foss.models.email_header": ["EmailHeader"],
    "aspose_jmap_foss.models.email": ["Email"],
    "aspose_jmap_foss.models.email_submission": ["EmailSubmission"],
    "aspose_jmap_foss.models.identity": ["Identity"],
    "aspose_jmap_foss.models.mailbox": ["Mailbox"],
    "aspose_jmap_foss.models.thread": ["Thread"],
    "aspose_jmap_foss.models.session": ["Session"],
    "aspose_jmap_foss.models.search_snippet": ["SearchSnippet"],
}

# Create stub modules and populate them with placeholder classes.
for full_name, class_names in _stub_modules.items():
    if full_name not in sys.modules:
        module = types.ModuleType(full_name)
        for cls_name in class_names:
            # Simple base class; for error types we inherit from Exception.
            base = Exception if cls_name.endswith("Error") else object
            setattr(module, cls_name, type(cls_name, (base,), {}))
        sys.modules[full_name] = module

# ----------------------------------------------------------------------
# Now import the public symbols under test.
# ----------------------------------------------------------------------
from aspose_jmap_foss import Address, Envelope


def test_address_full_round_trip() -> None:
    """An Address with all fields should deserialize and serialize unchanged."""
    json_data: Dict[str, Any] = {
        "email": "sender@example.com",
        "parameters": {"RET": "HDRS", "SIZE": None},
    }
    addr = Address.from_json(json_data)
    assert isinstance(addr, Address)
    assert addr.email == "sender@example.com"
    assert addr.parameters == {"RET": "HDRS", "SIZE": None}
    assert addr.to_json() == json_data


def test_address_missing_parameters() -> None:
    """When the optional `parameters` field is omitted it should become ``None``."""
    json_data: Dict[str, Any] = {"email": "rcpt@example.org"}
    addr = Address.from_json(json_data)
    assert isinstance(addr, Address)
    assert addr.email == "rcpt@example.org"
    assert addr.parameters is None
    # The model always emits the key, even when the value is ``None``.
    assert addr.to_json() == {"email": "rcpt@example.org", "parameters": None}


def test_envelope_round_trip_multiple_recipients() -> None:
    """Envelope with several recipients should round‑trip correctly."""
    json_data: Dict[str, Any] = {
        "mailFrom": {
            "email": "sender@example.com",
            "parameters": {"SIZE": "1234"},
        },
        "rcptTo": [
            {"email": "rcpt1@example.org", "parameters": None},
            {"email": "rcpt2@example.org", "parameters": {"RET": "FULL"}},
        ],
    }
    envelope = Envelope.from_json(json_data)
    assert isinstance(envelope, Envelope)
    # Verify inner Address objects.
    assert envelope.mail_from.email == "sender@example.com"
    assert envelope.mail_from.parameters == {"SIZE": "1234"}
    assert len(envelope.rcpt_to) == 2
    assert envelope.rcpt_to[0].email == "rcpt1@example.org"
    assert envelope.rcpt_to[0].parameters is None
    assert envelope.rcpt_to[1].email == "rcpt2@example.org"
    assert envelope.rcpt_to[1].parameters == {"RET": "FULL"}
    # Serializing back must reproduce the original JSON structure.
    assert envelope.to_json() == json_data


def test_envelope_empty_rcpt_to() -> None:
    """Edge case: an empty ``rcptTo`` list should be preserved through (de)serialization."""
    json_data: Dict[str, Any] = {
        "mailFrom": {"email": "sender@example.com"},
        "rcptTo": [],
    }
    envelope = Envelope.from_json(json_data)
    assert isinstance(envelope, Envelope)
    assert envelope.mail_from.email == "sender@example.com"
    assert envelope.mail_from.parameters is None
    assert envelope.rcpt_to == []
    # The serialized form must include the empty list and a null parameters field.
    expected_json: Dict[str, Any] = {
        "mailFrom": {"email": "sender@example.com", "parameters": None},
        "rcptTo": [],
    }
    assert envelope.to_json() == expected_json
