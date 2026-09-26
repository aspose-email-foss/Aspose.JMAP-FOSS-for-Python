"""EmailQueryResponse model for Mail module.

The full result of an Email/query call, per RFC 8620 section 5.5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class EmailQueryResponse:
    """Result of an Email/query call.

    Attributes:
        account_id: The id of the account used for the call.
        query_state: A string encoding the current state of the query.
        can_calculate_changes: ``True`` if it is possible, given the current
            query state, for the client to call ``Email/queryChanges`` to
            find out which items have been added/removed since the
            ``query_state``.
        position: The zero-based index of the first result in the ``ids``
            array within the complete list of query results.
        ids: The list of message ids matching the query, in the requested
            sort order, starting at ``position``.
        total: The total number of messages in the query results, if
            requested by the client. May be absent.
        limit: The limit that was applied to the query, if the server
            enforced one different to any limit requested by the client.
            May be absent.
    """

    account_id: str
    query_state: str
    can_calculate_changes: bool
    position: int
    ids: List[str]
    total: Optional[int] = None
    limit: Optional[int] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> EmailQueryResponse:
        """Create an :class:`EmailQueryResponse` from a JSON dictionary.

        Args:
            data: Mapping with keys ``accountId``, ``queryState``,
                ``canCalculateChanges``, ``position``, ``ids``, ``total``
                and ``limit``.

        Returns:
            An instance of :class:`EmailQueryResponse`.
        """
        return cls(
            account_id=data["accountId"],
            query_state=data["queryState"],
            can_calculate_changes=data.get("canCalculateChanges", False),
            position=data.get("position", 0),
            ids=data.get("ids", []),
            total=data.get("total"),
            limit=data.get("limit"),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the :class:`EmailQueryResponse` to a JSON-compatible dictionary.

        Returns:
            A dict with keys ``accountId``, ``queryState``,
            ``canCalculateChanges``, ``position``, ``ids``, ``total`` and
            ``limit``.
        """
        json_dict: Dict[str, Any] = {
            "accountId": self.account_id,
            "queryState": self.query_state,
            "canCalculateChanges": self.can_calculate_changes,
            "position": self.position,
            "ids": self.ids,
        }
        if self.total is not None:
            json_dict["total"] = self.total
        if self.limit is not None:
            json_dict["limit"] = self.limit
        return json_dict
