from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

__all__ = ["Thread"]


@dataclass
class Thread:
    """An ordered list of Email ids that make up a conversation."""

    # server-assigned; omit when constructing a create payload
    id: Optional[str] = None
    # server-assigned; omit when constructing a create payload
    email_ids: Optional[List[str]] = None

    @staticmethod
    def from_json(data: Dict[str, Any]) -> Thread:
        """Create a :class:`Thread` instance from a JSON dictionary."""
        return Thread(
            id=data.get("id"),
            email_ids=data.get("emailIds"),
        )

    def to_json(self) -> Dict[str, Any]:
        """Convert the :class:`Thread` instance to a JSON‑compatible dictionary."""
        result: Dict[str, Any] = {}
        if self.id is not None:
            result["id"] = self.id
        if self.email_ids is not None:
            result["emailIds"] = self.email_ids
        return result
