"""JMAP Session model definitions.

Defines dataclasses for the Session resource and its related sub‑objects
(Account and CoreCapability) with explicit JSON (de)serialization methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CoreCapability:
    """Capability object for ``urn:ietf:params:jmap:core``.

    All fields are required and map directly to the JMAP wire format.
    """

    max_size_upload: int
    max_concurrent_upload: int
    max_size_request: int
    max_concurrent_requests: int
    max_calls_in_request: int
    max_objects_in_get: int
    max_objects_in_set: int
    collation_algorithms: List[str]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> CoreCapability:
        """Create a :class:`CoreCapability` from a JMAP JSON dict."""
        return cls(
            max_size_upload=data["maxSizeUpload"],
            max_concurrent_upload=data["maxConcurrentUpload"],
            max_size_request=data["maxSizeRequest"],
            max_concurrent_requests=data["maxConcurrentRequests"],
            max_calls_in_request=data["maxCallsInRequest"],
            max_objects_in_get=data["maxObjectsInGet"],
            max_objects_in_set=data["maxObjectsInSet"],
            collation_algorithms=data["collationAlgorithms"],
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the instance to a JMAP‑compatible JSON dict."""
        return {
            "maxSizeUpload": self.max_size_upload,
            "maxConcurrentUpload": self.max_concurrent_upload,
            "maxSizeRequest": self.max_size_request,
            "maxConcurrentRequests": self.max_concurrent_requests,
            "maxCallsInRequest": self.max_calls_in_request,
            "maxObjectsInGet": self.max_objects_in_get,
            "maxObjectsInSet": self.max_objects_in_set,
            "collationAlgorithms": self.collation_algorithms,
        }


@dataclass
class Account:
    """Account object contained within a Session.

    Fields are optional because the JMAP spec does not require them for every
    account; they default to ``None`` or an empty mapping when absent.
    """

    name: str | None = None
    is_personal: bool | None = None
    is_read_only: bool | None = None
    account_capabilities: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Account:
        """Create an :class:`Account` from a JMAP JSON dict."""
        return cls(
            name=data.get("name"),
            is_personal=data.get("isPersonal"),
            is_read_only=data.get("isReadOnly"),
            account_capabilities=data.get("accountCapabilities", {}),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the instance to a JMAP‑compatible JSON dict."""
        json_dict: Dict[str, Any] = {}
        if self.name is not None:
            json_dict["name"] = self.name
        if self.is_personal is not None:
            json_dict["isPersonal"] = self.is_personal
        if self.is_read_only is not None:
            json_dict["isReadOnly"] = self.is_read_only
        if self.account_capabilities:
            json_dict["accountCapabilities"] = self.account_capabilities
        return json_dict


@dataclass
class Session:
    """JMAP Session resource describing server capabilities and endpoints."""

    capabilities: Dict[str, Any]
    accounts: Dict[str, Account]
    primary_accounts: Dict[str, str]
    username: str
    api_url: str
    download_url: str
    upload_url: str
    event_source_url: str
    state: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Session:
        """Create a :class:`Session` from a JMAP JSON dict."""
        accounts = {
            acc_id: Account.from_json(acc_json)
            for acc_id, acc_json in data["accounts"].items()
        }

        return cls(
            capabilities=data["capabilities"],
            accounts=accounts,
            primary_accounts=data["primaryAccounts"],
            username=data["username"],
            api_url=data["apiUrl"],
            download_url=data["downloadUrl"],
            upload_url=data["uploadUrl"],
            event_source_url=data["eventSourceUrl"],
            state=data["state"],
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the instance to a JMAP‑compatible JSON dict."""
        return {
            "capabilities": self.capabilities,
            "accounts": {aid: acc.to_json() for aid, acc in self.accounts.items()},
            "primaryAccounts": self.primary_accounts,
            "username": self.username,
            "apiUrl": self.api_url,
            "downloadUrl": self.download_url,
            "uploadUrl": self.upload_url,
            "eventSourceUrl": self.event_source_url,
            "state": self.state,
        }


__all__ = ("Session", "Account", "CoreCapability")
