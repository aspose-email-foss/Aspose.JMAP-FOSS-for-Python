"""Models for JMAP request envelope."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from .invocation import Invocation


@dataclass(init=False)
class JmapRequestEnvelope:
    """The JSON body POSTed to Session.apiUrl.

    Attributes:
        using: Capability URNs this request depends on, must include
            ``urn:ietf:params:jmap:core``.
        method_calls: List of method invocations to execute.
        created_ids: Mapping from client‑generated IDs to server‑assigned IDs,
            or ``None`` if not present.
    """

    using: List[str]
    method_calls: List[Invocation] = field(default_factory=list)
    created_ids: Optional[Dict[str, str]] = None

    def __init__(
        self,
        using: List[str],
        method_calls: List[Invocation] | None = None,
        created_ids: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new envelope.

        Accepts both snake_case and camelCase keyword arguments for compatibility.
        """
        # Support camelCase aliases
        if method_calls is None and "methodCalls" in kwargs:
            method_calls = kwargs.pop("methodCalls")
        if created_ids is None and "createdIds" in kwargs:
            created_ids = kwargs.pop("createdIds")

        if kwargs:
            unexpected = ", ".join(kwargs.keys())
            raise TypeError(f"Unexpected argument(s): {unexpected}")

        self.using = using
        self.method_calls = method_calls if method_calls is not None else []
        self.created_ids = created_ids

    # --------------------------------------------------------------------- #
    # Compatibility properties (camelCase)                                 #
    # --------------------------------------------------------------------- #
    @property
    def methodCalls(self) -> List[Invocation]:
        """CamelCase alias for :attr:`method_calls`."""
        return self.method_calls

    @methodCalls.setter
    def methodCalls(self, value: List[Invocation]) -> None:
        self.method_calls = value

    @property
    def createdIds(self) -> Optional[Dict[str, str]]:
        """CamelCase alias for :attr:`created_ids`."""
        return self.created_ids

    @createdIds.setter
    def createdIds(self, value: Optional[Dict[str, str]]) -> None:
        self.created_ids = value

    # --------------------------------------------------------------------- #
    # JSON (de)serialization                                                #
    # --------------------------------------------------------------------- #
    @classmethod
    def from_json(cls, data: dict) -> JmapRequestEnvelope:
        """Create an instance from a JSON‑decoded dict.

        Args:
            data: The JSON object representing the request envelope.

        Returns:
            A :class:`JmapRequestEnvelope` instance.
        """
        using = list(data["using"])
        method_calls = [Invocation.from_json(item) for item in data["methodCalls"]]
        created_ids_raw = data.get("createdIds")
        created_ids = (
            {k: v for k, v in created_ids_raw.items()} if isinstance(created_ids_raw, dict) else None
        )
        return cls(using=using, method_calls=method_calls, created_ids=created_ids)

    def to_json(self) -> dict:
        """Serialize the envelope to a JSON‑compatible dict.

        Returns:
            A dict ready for ``json.dumps`` that follows the JMAP wire format.
        """
        return {
            "using": self.using,
            "methodCalls": [invocation.to_json() for invocation in self.method_calls],
            "createdIds": self.created_ids,
        }
