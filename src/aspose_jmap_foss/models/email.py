from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from .email_address import EmailAddress
from .email_body_part import EmailBodyPart


@dataclass
class EmailBodyValue:
    """Represents a body value with optional encoding problem and truncation flags."""

    value: str
    is_encoding_problem: bool
    is_truncated: bool

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> EmailBodyValue:
        """Create an ``EmailBodyValue`` instance from its JMAP JSON representation."""
        return cls(
            value=data["value"],
            is_encoding_problem=data["isEncodingProblem"],
            is_truncated=data["isTruncated"],
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize this ``EmailBodyValue`` to the JMAP JSON representation."""
        return {
            "value": self.value,
            "isEncodingProblem": self.is_encoding_problem,
            "isTruncated": self.is_truncated,
        }


@dataclass
class Email:
    """A single email message (RFC 8621 ``Email`` object). Immutable content (headers,
    body) plus mutable per‑mailbox metadata (mailboxIds, keywords)."""

    # Server‑assigned identifiers (omit when constructing a create payload)
    id: Optional[str] = None
    blob_id: Optional[str] = None
    thread_id: Optional[str] = None

    # Required mutable metadata
    mailbox_ids: Dict[str, bool] = field(default_factory=dict)

    # Optional mutable metadata
    keywords: Dict[str, bool] = field(default_factory=dict)

    # Server‑assigned immutable metadata (omit when constructing a create payload)
    size: Optional[int] = None
    received_at: Optional[str] = None  # UTCDate as RFC 3339 string

    # Header fields
    message_id: Optional[List[str]] = None
    in_reply_to: Optional[List[str]] = None
    references: Optional[List[str]] = None

    # Address fields
    sender: Optional[List[EmailAddress]] = None
    from_: Optional[List[EmailAddress]] = None  # ``from`` is a Python keyword
    to: Optional[List[EmailAddress]] = None
    cc: Optional[List[EmailAddress]] = None
    bcc: Optional[List[EmailAddress]] = None
    reply_to: Optional[List[EmailAddress]] = None

    # Miscellaneous fields
    subject: Optional[str] = None
    sent_at: Optional[str] = None  # Date as RFC 3339 string

    # Body structure (server‑assigned)
    body_structure: Optional[EmailBodyPart] = None
    body_values: Dict[str, EmailBodyValue] = field(default_factory=dict)
    text_body: List[EmailBodyPart] = field(default_factory=list)
    html_body: List[EmailBodyPart] = field(default_factory=list)
    attachments: List[EmailBodyPart] = field(default_factory=list)
    has_attachment: Optional[bool] = None
    preview: Optional[str] = None

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> Email:
        """Create an ``Email`` instance from its JMAP JSON representation."""
        return cls(
            id=data.get("id"),
            blob_id=data.get("blobId"),
            thread_id=data.get("threadId"),
            mailbox_ids=dict(data["mailboxIds"]),
            keywords=dict(data.get("keywords", {})),
            size=data.get("size"),
            received_at=data.get("receivedAt"),
            message_id=data.get("messageId"),
            in_reply_to=data.get("inReplyTo"),
            references=data.get("references"),
            sender=[EmailAddress.from_json(v) for v in data.get("sender", [])] or None,
            from_=[EmailAddress.from_json(v) for v in data.get("from", [])] or None,
            to=[EmailAddress.from_json(v) for v in data.get("to", [])] or None,
            cc=[EmailAddress.from_json(v) for v in data.get("cc", [])] or None,
            bcc=[EmailAddress.from_json(v) for v in data.get("bcc", [])] or None,
            reply_to=[EmailAddress.from_json(v) for v in data.get("replyTo", [])] or None,
            subject=data.get("subject"),
            sent_at=data.get("sentAt"),
            body_structure=EmailBodyPart.from_json(data["bodyStructure"])
            if "bodyStructure" in data
            else None,
            body_values={
                k: EmailBodyValue.from_json(v) for k, v in data.get("bodyValues", {}).items()
            },
            text_body=[EmailBodyPart.from_json(v) for v in data.get("textBody", [])],
            html_body=[EmailBodyPart.from_json(v) for v in data.get("htmlBody", [])],
            attachments=[EmailBodyPart.from_json(v) for v in data.get("attachments", [])],
            has_attachment=data.get("hasAttachment"),
            preview=data.get("preview"),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize this ``Email`` to the JMAP JSON representation."""
        result: Dict[str, Any] = {"mailboxIds": self.mailbox_ids}

        if self.id is not None:
            result["id"] = self.id
        if self.blob_id is not None:
            result["blobId"] = self.blob_id
        if self.thread_id is not None:
            result["threadId"] = self.thread_id
        if self.keywords:
            result["keywords"] = self.keywords
        if self.size is not None:
            result["size"] = self.size
        if self.received_at is not None:
            result["receivedAt"] = self.received_at
        if self.message_id is not None:
            result["messageId"] = self.message_id
        if self.in_reply_to is not None:
            result["inReplyTo"] = self.in_reply_to
        if self.references is not None:
            result["references"] = self.references
        if self.sender is not None:
            result["sender"] = [addr.to_json() for addr in self.sender]
        if self.from_ is not None:
            result["from"] = [addr.to_json() for addr in self.from_]
        if self.to is not None:
            result["to"] = [addr.to_json() for addr in self.to]
        if self.cc is not None:
            result["cc"] = [addr.to_json() for addr in self.cc]
        if self.bcc is not None:
            result["bcc"] = [addr.to_json() for addr in self.bcc]
        if self.reply_to is not None:
            result["replyTo"] = [addr.to_json() for addr in self.reply_to]
        if self.subject is not None:
            result["subject"] = self.subject
        if self.sent_at is not None:
            result["sentAt"] = self.sent_at
        if self.body_structure is not None:
            result["bodyStructure"] = self.body_structure.to_json()
        if self.body_values:
            result["bodyValues"] = {k: v.to_json() for k, v in self.body_values.items()}
        if self.text_body:
            result["textBody"] = [part.to_json() for part in self.text_body]
        if self.html_body:
            result["htmlBody"] = [part.to_json() for part in self.html_body]
        if self.attachments:
            result["attachments"] = [part.to_json() for part in self.attachments]
        if self.has_attachment is not None:
            result["hasAttachment"] = self.has_attachment
        if self.preview is not None:
            result["preview"] = self.preview

        return result
