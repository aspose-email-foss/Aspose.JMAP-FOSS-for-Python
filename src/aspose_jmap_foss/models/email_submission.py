from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .delivery_status import DeliveryStatus
from .envelope import Envelope


@dataclass
class EmailSubmission:
    """
    One attempt to submit an Email for delivery. Analogous to what Aspose.Email's
    SmtpClient.Send does synchronously over SMTP; here creating an EmailSubmission
    is what actually dispatches the message via the server's outbound MTA.
    """

    # required
    identity_id: str = field(metadata={"description": "Must reference an existing Identity"})
    # required
    email_id: str = field(metadata={"description": "The Email to send; typically a draft created via Email/set just before this call"})
    # server-assigned; omit when constructing a create payload
    id: Optional[str] = field(default=None, metadata={"description": "server-assigned, omit when constructing a create payload"})
    # server-assigned; omit when constructing a create payload
    thread_id: Optional[str] = field(default=None, metadata={"description": "server-assigned, omit when constructing a create payload"})
    envelope: Optional[Envelope] = None
    # server-assigned; omit when constructing a create payload
    send_at: Optional[str] = None
    # server-assigned; omit when constructing a create payload
    undo_status: Optional[str] = None
    # server-assigned; omit when constructing a create payload
    delivery_status: Optional[Dict[str, DeliveryStatus]] = None
    # server-assigned; omit when constructing a create payload
    dsn_blob_ids: Optional[List[str]] = None
    # server-assigned; omit when constructing a create payload
    mdn_blob_ids: Optional[List[str]] = None

    @classmethod
    def from_json(cls, data: dict) -> EmailSubmission:
        """Create an EmailSubmission instance from its JMAP JSON representation."""
        return cls(
            id=data.get("id"),
            identity_id=data["identityId"],
            email_id=data["emailId"],
            thread_id=data.get("threadId"),
            envelope=Envelope.from_json(data["envelope"]) if data.get("envelope") is not None else None,
            send_at=data.get("sendAt"),
            undo_status=data.get("undoStatus"),
            delivery_status=(
                {k: DeliveryStatus.from_json(v) for k, v in data["deliveryStatus"].items()}
                if data.get("deliveryStatus") is not None
                else None
            ),
            dsn_blob_ids=data.get("dsnBlobIds"),
            mdn_blob_ids=data.get("mdnBlobIds"),
        )

    def to_json(self) -> dict:
        """Serialize the EmailSubmission instance to its JMAP JSON representation."""
        result: dict = {
            "identityId": self.identity_id,
            "emailId": self.email_id,
        }
        if self.id is not None:
            result["id"] = self.id
        if self.thread_id is not None:
            result["threadId"] = self.thread_id
        if self.envelope is not None:
            result["envelope"] = self.envelope.to_json()
        if self.send_at is not None:
            result["sendAt"] = self.send_at
        if self.undo_status is not None:
            result["undoStatus"] = self.undo_status
        if self.delivery_status is not None:
            result["deliveryStatus"] = {k: v.to_json() for k, v in self.delivery_status.items()}
        if self.dsn_blob_ids is not None:
            result["dsnBlobIds"] = self.dsn_blob_ids
        if self.mdn_blob_ids is not None:
            result["mdnBlobIds"] = self.mdn_blob_ids
        return result
