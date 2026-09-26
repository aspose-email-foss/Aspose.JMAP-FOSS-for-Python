"""Models for the JMAP Submission envelope."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Address:
    """SMTP address with optional parameters."""

    email: str
    parameters: Optional[Dict[str, Optional[str]]] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Address":
        """Create an :class:`Address` from its JMAP JSON representation."""
        email = data["email"]
        parameters = data.get("parameters")
        return cls(email=email, parameters=parameters)

    def to_json(self) -> Dict[str, Any]:
        """Serialize the :class:`Address` to its JMAP JSON representation."""
        return {
            "email": self.email,
            "parameters": self.parameters,
        }


@dataclass
class Envelope:
    """SMTP MAIL FROM / RCPT TO envelope for a submission, distinct from the message's own From/To headers."""

    mail_from: Address
    rcpt_to: List[Address]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Envelope":
        """Create an :class:`Envelope` from its JMAP JSON representation."""
        mail_from = Address.from_json(data["mailFrom"])
        rcpt_to = [Address.from_json(item) for item in data["rcptTo"]]
        return cls(mail_from=mail_from, rcpt_to=rcpt_to)

    def to_json(self) -> Dict[str, Any]:
        """Serialize the :class:`Envelope` to its JMAP JSON representation."""
        return {
            "mailFrom": self.mail_from.to_json(),
            "rcptTo": [addr.to_json() for addr in self.rcpt_to],
        }
