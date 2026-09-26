"""Tests for the Mailbox and MailboxRights model classes.

The package's top‑level ``aspose_jmap_foss`` imports many symbols that are not
present in this kata.  To keep the test suite importable we provide minimal stub
modules for the missing symbols before importing the public package.
"""

from __future__ import annotations

import sys
import types
from typing import Any, Dict

# --------------------------------------------------------------------------- #
# Stub out missing modules so that ``aspose_jmap_foss.__init__`` can be imported
# without raising ImportError.  Only the names required by the package initializer
# are defined; they are simple placeholders and are not used by the Mailbox tests.
# --------------------------------------------------------------------------- #

def _stub_module(name: str, attrs: Dict[str, Any] | None = None) -> types.ModuleType:
    """Create a dummy module with optional attributes."""
    if name in sys.modules:
        return sys.modules[name]  # already stubbed
    mod = types.ModuleType(name)
    if attrs:
        for attr_name, attr_val in attrs.items():
            setattr(mod, attr_name, attr_val)
    sys.modules[name] = mod
    return mod


# core error types expected by ``aspose_jmap_foss.client_core``
class JmapError(Exception):
    """Base class for JMAP errors (stub)."""


class JmapNetworkError(JmapError):
    """Network‑related error (stub)."""


class JmapProtocolError(JmapError):
    """Protocol‑related error (stub)."""

    def __init__(self, type_: str, description: str) -> None:
        super().__init__(description)
        self.type = type_
        self.description = description


_stub_module(
    "aspose_jmap_foss.common_types",
    {
        "JmapError": JmapError,
        "JmapNetworkError": JmapNetworkError,
        "JmapProtocolError": JmapProtocolError,
    },
)

# ``aspose_jmap_foss.models`` package and its sub‑modules that are otherwise missing
_models_pkg = _stub_module("aspose_jmap_foss.models")
_models_pkg.__path__ = []  # mark as a package

# stub a handful of model sub‑modules that the public ``__init__`` re‑exports
for _mod_name in (
    "delivery_status",
    "email",
    "email_address",
    "email_address_group",
    "email_body_part",
    "email_header",
    "comparator",
    "invocation",
):
    _stub_module(f"aspose_jmap_foss.models.{_mod_name}", {})

# --------------------------------------------------------------------------- #
# Import the public symbols under test.
# --------------------------------------------------------------------------- #

from aspose_jmap_foss import Mailbox, MailboxRights


def test_mailbox_rights_serialization_roundtrip() -> None:
    """MailboxRights should round‑trip through JSON unchanged."""
    rights = MailboxRights(
        may_read_items=True,
        may_add_items=False,
        may_remove_items=True,
        may_set_seen=False,
        may_set_keywords=True,
        may_create_child=False,
        may_rename=True,
        may_delete=False,
        may_submit=True,
    )
    json_data = rights.to_json()
    assert json_data == {
        "mayReadItems": True,
        "mayAddItems": False,
        "mayRemoveItems": True,
        "maySetSeen": False,
        "maySetKeywords": True,
        "mayCreateChild": False,
        "mayRename": True,
        "mayDelete": False,
        "maySubmit": True,
    }

    recreated = MailboxRights.from_json(json_data)
    assert recreated == rights


def test_mailbox_full_serialization_roundtrip() -> None:
    """A fully populated Mailbox should round‑trip through JSON unchanged."""
    rights = MailboxRights(
        may_read_items=True,
        may_add_items=True,
        may_remove_items=True,
        may_set_seen=True,
        may_set_keywords=True,
        may_create_child=True,
        may_rename=True,
        may_delete=True,
        may_submit=True,
    )
    mailbox = Mailbox(
        id="mailbox123",
        name="Inbox",
        parent_id="parent456",
        role="inbox",
        sort_order=10,
        total_emails=100,
        unread_emails=5,
        total_threads=80,
        unread_threads=3,
        my_rights=rights,
        is_subscribed=True,
    )
    json_data = mailbox.to_json()
    expected = {
        "id": "mailbox123",
        "name": "Inbox",
        "parentId": "parent456",
        "role": "inbox",
        "sortOrder": 10,
        "totalEmails": 100,
        "unreadEmails": 5,
        "totalThreads": 80,
        "unreadThreads": 3,
        "myRights": rights.to_json(),
        "isSubscribed": True,
    }
    assert json_data == expected

    recreated = Mailbox.from_json(json_data)
    assert recreated == mailbox


def test_mailbox_deserialize_minimal() -> None:
    """Deserialization must handle missing optional fields and apply defaults."""
    json_input = {"name": "Drafts"}  # only the required field
    mailbox = Mailbox.from_json(json_input)

    # required field
    assert mailbox.name == "Drafts"
    # optional fields default to None or their defined defaults
    assert mailbox.id is None
    assert mailbox.parent_id is None
    assert mailbox.role is None
    assert mailbox.sort_order == 0
    assert mailbox.total_emails is None
    assert mailbox.unread_emails is None
    assert mailbox.total_threads is None
    assert mailbox.unread_threads is None
    assert mailbox.my_rights is None
    assert mailbox.is_subscribed is False

    # to_json should omit all None fields and include only the required defaults
    json_output = mailbox.to_json()
    assert json_output == {
        "name": "Drafts",
        "sortOrder": 0,
        "isSubscribed": False,
    }


def test_mailbox_serialization_without_rights() -> None:
    """When ``my_rights`` is omitted, it must not appear in the JSON output."""
    mailbox = Mailbox(name="Sent", is_subscribed=False)
    json_data = mailbox.to_json()
    # ``myRights`` must be absent because the attribute is ``None``.
    assert "myRights" not in json_data
    # other fields follow the default handling rules
    assert json_data == {
        "name": "Sent",
        "sortOrder": 0,
        "isSubscribed": False,
    }

    # recreating from the minimal JSON must yield an equivalent object
    recreated = Mailbox.from_json(json_data)
    assert recreated == mailbox
