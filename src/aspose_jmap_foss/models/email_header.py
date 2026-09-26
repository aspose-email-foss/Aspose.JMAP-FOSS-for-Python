"""EmailHeader model representing a name/value pair in an email header."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Type


__all__ = ["EmailHeader"]


@dataclass
class EmailHeader:
    """Represents an email header with a name and its corresponding value."""

    name: str
    """The header name."""

    value: str
    """The header value."""

    @classmethod
    def from_json(cls: Type["EmailHeader"], data: Dict[str, Any]) -> "EmailHeader":
        """
        Create an EmailHeader instance from its JSON representation.

        Args:
            data: A dict containing the JMAP wire format keys ``name`` and ``value``.

        Returns:
            An EmailHeader instance.
        """
        return cls(
            name=data["name"],
            value=data["value"],
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Convert this EmailHeader to its JSON representation.

        Returns:
            A dict with keys ``name`` and ``value`` suitable for JMAP transmission.
        """
        return {
            "name": self.name,
            "value": self.value,
        }
