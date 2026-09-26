"""Comparator model for Mail module.

One entry of an Email/query 'sort' argument.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class Comparator:
    """Comparator used to define sorting for Email/query.

    Attributes:
        property: The name of the property to sort by (e.g. ``receivedAt``,
            ``from``, ``subject``, ``size``).
        is_ascending: ``True`` for ascending order, ``False`` for descending.
            Defaults to ``True``.
        collation: Optional collation identifier for locale‑aware sorting.
    """

    property: str
    is_ascending: bool = field(default=True, metadata={"json_name": "isAscending"})
    collation: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Comparator:
        """Create a :class:`Comparator` from a JSON dictionary.

        Args:
            data: Mapping with keys ``property``, ``isAscending`` and ``collation``.

        Returns:
            An instance of :class:`Comparator`.
        """
        return cls(
            property=data["property"],
            is_ascending=data.get("isAscending", True),
            collation=data.get("collation"),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the :class:`Comparator` to a JSON‑compatible dictionary.

        Returns:
            A dict with keys ``property``, ``isAscending`` and ``collation``.
        """
        json_dict: Dict[str, Any] = {
            "property": self.property,
            "isAscending": self.is_ascending,
        }
        if self.collation is not None:
            json_dict["collation"] = self.collation
        return json_dict
