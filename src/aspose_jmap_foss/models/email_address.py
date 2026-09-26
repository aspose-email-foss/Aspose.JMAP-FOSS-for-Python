"""Model definitions for the Mail module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, TypedDict


@dataclass
class EmailAddress:
    """One address in a header such as From/To/Cc (RFC 8621 section 4.1.2.3)."""

    name: Optional[str] = None
    """The display name associated with the address. May be null."""

    email: str = ""
    """The email address (required)."""

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> EmailAddress:
        """
        Create an :class:`EmailAddress` instance from a JSON object.

        Args:
            data: Mapping containing the JMAP wire format fields.

        Returns:
            An ``EmailAddress`` populated from *data*.
        """
        return cls(
            name=data.get("name"),
            email=data["email"],
        )

    def to_json(self) -> dict[str, Any]:
        """
        Convert this ``EmailAddress`` to a JSON‑compatible dict using JMAP field names.

        Returns:
            A dict with keys ``name`` and ``email`` suitable for serialization.
        """
        return {
            "name": self.name,
            "email": self.email,
        }
