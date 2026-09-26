from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .email_address import EmailAddress


@dataclass
class EmailAddressGroup:
    """Group syntax as in From/To headers, e.g. 'Team: a@x, b@x;'."""

    name: Optional[str]
    addresses: List[EmailAddress]

    @staticmethod
    def from_json(data: dict) -> EmailAddressGroup:
        """
        Create an ``EmailAddressGroup`` instance from its JMAP JSON representation.

        Args:
            data: A dict containing the keys ``name`` and ``addresses`` as defined by the JMAP spec.

        Returns:
            An ``EmailAddressGroup`` populated with the supplied data.
        """
        name = data.get("name")
        addresses_data = data.get("addresses", [])
        addresses = [EmailAddress.from_json(item) for item in addresses_data]
        return EmailAddressGroup(name=name, addresses=addresses)

    def to_json(self) -> dict:
        """
        Convert this ``EmailAddressGroup`` instance to its JMAP JSON representation.

        Returns:
            A dict with keys ``name`` and ``addresses`` suitable for transmission to a JMAP server.
        """
        return {
            "name": self.name,
            "addresses": [addr.to_json() for addr in self.addresses],
        }
