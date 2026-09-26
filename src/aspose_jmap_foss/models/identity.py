from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .email_address import EmailAddress


@dataclass
class Identity:
    """A sending identity (name/email/replyTo used as the From when submitting mail);
    analogous to configuring a MailAddress + display name on Aspose's SmtpClient.
    """

    # required fields (no default)
    email: str

    # optional / server‑assigned fields
    id: Optional[str] = field(default=None, metadata={"description": "server-assigned, omit when constructing a create payload"})
    name: str = field(default="", metadata={"description": "display name"})
    reply_to: Optional[List[EmailAddress]] = field(default=None, metadata={"description": "list of reply‑to addresses"})
    bcc: Optional[List[EmailAddress]] = field(default=None, metadata={"description": "list of BCC addresses"})
    text_signature: str = field(default="", metadata={"description": "plain‑text signature"})
    html_signature: str = field(default="", metadata={"description": "HTML signature"})
    may_delete: Optional[bool] = field(default=None, metadata={"description": "server-assigned, omit when constructing a create payload"})

    @staticmethod
    def from_json(data: dict) -> Identity:
        """Create an :class:`Identity` instance from a JMAP JSON object."""
        return Identity(
            email=data["email"],
            id=data.get("id"),
            name=data.get("name", ""),
            reply_to=(
                [EmailAddress.from_json(item) for item in data["replyTo"]]
                if data.get("replyTo") is not None
                else None
            ),
            bcc=(
                [EmailAddress.from_json(item) for item in data["bcc"]]
                if data.get("bcc") is not None
                else None
            ),
            text_signature=data.get("textSignature", ""),
            html_signature=data.get("htmlSignature", ""),
            may_delete=data.get("mayDelete"),
        )

    def to_json(self) -> dict:
        """Serialize this :class:`Identity` to a JMAP‑compatible JSON dict."""
        result: dict = {"email": self.email}
        if self.id is not None:
            result["id"] = self.id
        result["name"] = self.name
        if self.reply_to is not None:
            result["replyTo"] = [addr.to_json() for addr in self.reply_to]
        if self.bcc is not None:
            result["bcc"] = [addr.to_json() for addr in self.bcc]
        result["textSignature"] = self.text_signature
        result["htmlSignature"] = self.html_signature
        if self.may_delete is not None:
            result["mayDelete"] = self.may_delete
        return result
