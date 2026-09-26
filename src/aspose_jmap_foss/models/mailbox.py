"""Models for JMAP Mailbox and related types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class MailboxRights:
    """Rights a user has on a mailbox.

    All fields are required booleans as defined by the JMAP specification.
    """

    may_read_items: bool
    may_add_items: bool
    may_remove_items: bool
    may_set_seen: bool
    may_set_keywords: bool
    may_create_child: bool
    may_rename: bool
    may_delete: bool
    may_submit: bool

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> MailboxRights:
        """Create a :class:`MailboxRights` instance from a JSON dict."""
        return cls(
            may_read_items=data["mayReadItems"],
            may_add_items=data["mayAddItems"],
            may_remove_items=data["mayRemoveItems"],
            may_set_seen=data["maySetSeen"],
            may_set_keywords=data["maySetKeywords"],
            may_create_child=data["mayCreateChild"],
            may_rename=data["mayRename"],
            may_delete=data["mayDelete"],
            may_submit=data["maySubmit"],
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the instance to a JSON‑compatible dict."""
        return {
            "mayReadItems": self.may_read_items,
            "mayAddItems": self.may_add_items,
            "mayRemoveItems": self.may_remove_items,
            "maySetSeen": self.may_set_seen,
            "maySetKeywords": self.may_set_keywords,
            "mayCreateChild": self.may_create_child,
            "mayRename": self.may_rename,
            "mayDelete": self.may_delete,
            "maySubmit": self.may_submit,
        }


@dataclass
class Mailbox:
    """A named set of Emails (JMAP's analogue of a mail folder / IMAP mailbox)."""

    # server‑assigned, omit when constructing a create payload
    id: Optional[str] = field(default=None, metadata={"description": "server-assigned; do not set when constructing a create payload"})
    # required
    name: str = field(default="")
    parent_id: Optional[str] = None
    role: Optional[str] = None
    sort_order: int = 0
    total_emails: Optional[int] = None  # server‑assigned
    unread_emails: Optional[int] = None  # server‑assigned
    total_threads: Optional[int] = None  # server‑assigned
    unread_threads: Optional[int] = None  # server‑assigned
    my_rights: Optional[MailboxRights] = None  # server‑assigned
    is_subscribed: bool = False

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Mailbox:
        """Create a :class:`Mailbox` instance from a JSON dict."""
        return cls(
            id=data.get("id"),
            name=data["name"],
            parent_id=data.get("parentId"),
            role=data.get("role"),
            sort_order=data.get("sortOrder", 0),
            total_emails=data.get("totalEmails"),
            unread_emails=data.get("unreadEmails"),
            total_threads=data.get("totalThreads"),
            unread_threads=data.get("unreadThreads"),
            my_rights=MailboxRights.from_json(data["myRights"]) if "myRights" in data else None,
            is_subscribed=data.get("isSubscribed", False),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the instance to a JSON‑compatible dict.

        Fields with a value of ``None`` are omitted, matching JMAP's expectations for
        create/update payloads.
        """
        result: Dict[str, Any] = {
            "name": self.name,
            "sortOrder": self.sort_order,
            "isSubscribed": self.is_subscribed,
        }

        if self.id is not None:
            result["id"] = self.id
        if self.parent_id is not None:
            result["parentId"] = self.parent_id
        if self.role is not None:
            result["role"] = self.role
        if self.total_emails is not None:
            result["totalEmails"] = self.total_emails
        if self.unread_emails is not None:
            result["unreadEmails"] = self.unread_emails
        if self.total_threads is not None:
            result["totalThreads"] = self.total_threads
        if self.unread_threads is not None:
            result["unreadThreads"] = self.unread_threads
        if self.my_rights is not None:
            result["myRights"] = self.my_rights.to_json()

        return result
