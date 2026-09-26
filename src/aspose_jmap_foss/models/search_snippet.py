"""Models for the Mail module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SearchSnippet:
    """Highlighted subject/preview snippet for an Email id matched by a filter's text search."""
    email_id: str
    subject: Optional[str] = None
    preview: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> SearchSnippet:
        """
        Create a :class:`SearchSnippet` instance from a JSON dictionary.

        Args:
            data: The JSON dictionary with JMAP wire format keys.

        Returns:
            A populated :class:`SearchSnippet` object.
        """
        return cls(
            email_id=data["emailId"],
            subject=data.get("subject"),
            preview=data.get("preview"),
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert this :class:`SearchSnippet` instance to a JSON‑compatible dictionary
        using JMAP wire format keys.

        Returns:
            A dictionary ready for JSON serialization.
        """
        return {
            "emailId": self.email_id,
            "subject": self.subject,
            "preview": self.preview,
        }
