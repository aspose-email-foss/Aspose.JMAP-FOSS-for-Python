"""JMAP response envelope model.

The JSON body returned from the JMAP `apiUrl`.  This class mirrors the wire format
exactly, using the original property names (`methodResponses`, `createdIds`,
`sessionState`) as JSON keys while exposing snake_case attributes in Python.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .invocation import Invocation


@dataclass
class JmapResponseEnvelope:
    """The JSON body returned from apiUrl.

    Deliberately NOT named bare "Response" for the same reason
    JmapRequestEnvelope isn't named "Request".
    """

    method_responses: List[Invocation]
    created_ids: Optional[Dict[str, str]] = None
    session_state: str = ""

    @classmethod
    def from_json(cls, data: dict) -> JmapResponseEnvelope:
        """Create an instance from a JSON dictionary."""
        method_responses = [
            Invocation.from_json(item) for item in data["methodResponses"]
        ]

        created_ids = (
            {k: v for k, v in data["createdIds"].items()}
            if "createdIds" in data and data["createdIds"] is not None
            else None
        )

        session_state = data["sessionState"]

        return cls(
            method_responses=method_responses,
            created_ids=created_ids,
            session_state=session_state,
        )

    def to_json(self) -> dict:
        """Serialize the instance to a JSON‑compatible dictionary."""
        result: dict = {
            "methodResponses": [inv.to_json() for inv in self.method_responses],
            "sessionState": self.session_state,
        }
        if self.created_ids is not None:
            result["createdIds"] = self.created_ids
        return result
