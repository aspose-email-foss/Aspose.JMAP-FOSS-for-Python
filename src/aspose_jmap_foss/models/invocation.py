"""JMAP method invocation model.

Represents a single method call tuple ``[name, arguments, methodCallId]`` used in
request and response envelopes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Invocation:
    """A JMAP method invocation.

    Attributes
    ----------
    name:
        The JMAP method name (e.g. ``Email/get``).
    arguments:
        Mapping of argument names to JSON‑compatible values.
    method_call_id:
        Client‑chosen identifier echoed back in the response.
    """

    name: str
    arguments: Dict[str, Any]
    method_call_id: str

    @classmethod
    def from_json(cls, data: List[Any]) -> Invocation:
        """Create an :class:`Invocation` from its JSON array representation.

        Parameters
        ----------
        data:
            A three‑element list ``[name, arguments, methodCallId]``.

        Returns
        -------
        Invocation
            The populated instance.

        Raises
        ------
        ValueError
            If *data* is not a three‑element list.
        """
        if not isinstance(data, list) or len(data) != 3:
            raise ValueError("Invocation JSON must be a list of three elements")
        name, arguments, method_call_id = data
        return cls(name=name, arguments=arguments, method_call_id=method_call_id)

    def to_json(self) -> List[Any]:
        """Serialize the :class:`Invocation` to the JMAP JSON array format."""
        return [self.name, self.arguments, self.method_call_id]
