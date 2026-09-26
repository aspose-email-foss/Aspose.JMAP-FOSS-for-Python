"""Models for the Submission module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DeliveryStatus:
    """Per-recipient delivery outcome, keyed by recipient email address on EmailSubmission.deliveryStatus.

    Attributes:
        smtp_reply: The raw SMTP reply string.
        delivered: Delivery status – one of ``queued``, ``yes``, ``no`` or ``unknown``.
        displayed: Display status – either ``unknown`` or ``yes``.
    """

    smtp_reply: str
    delivered: str
    displayed: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> DeliveryStatus:
        """Create a :class:`DeliveryStatus` instance from a JMAP JSON object.

        Args:
            data: Dictionary parsed from JSON with camelCase keys.

        Returns:
            DeliveryStatus: The populated model instance.
        """
        return cls(
            smtp_reply=data.get("smtpReply", ""),
            delivered=data.get("delivered", ""),
            displayed=data.get("displayed", ""),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the :class:`DeliveryStatus` instance to a JMAP‑compatible JSON dict.

        Returns:
            dict: Mapping of camelCase property names to their values.
        """
        return {
            "smtpReply": self.smtp_reply,
            "delivered": self.delivered,
            "displayed": self.displayed,
        }
