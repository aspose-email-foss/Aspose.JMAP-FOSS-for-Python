"""Common JMAP types and error hierarchy.

This module defines shared data shapes used across the JMAP client library
(`SetError`, `MethodError`, `ResultReference`) and the exception hierarchy
(`JmapError`, `JmapProtocolError`, `JmapNetworkError`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ----------------------------------------------------------------------
# Model classes
# ----------------------------------------------------------------------


@dataclass
class SetError:
    """Standard error shape returned per‑id in `notCreated`, `notUpdated`, `notDestroyed`.

    Attributes:
        type: Machine‑readable error identifier (e.g. ``invalidProperties``).
        description: Human‑readable description, may be ``None``.
        properties: List of property names that caused the error, may be ``None``.
    """

    type: str
    description: Optional[str] = None
    properties: Optional[List[str]] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> SetError:
        """Create a :class:`SetError` from its JSON representation."""
        return cls(
            type=data["type"],
            description=data.get("description"),
            properties=data.get("properties"),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the instance to a JSON‑compatible ``dict``."""
        result: Dict[str, Any] = {"type": self.type}
        if self.description is not None:
            result["description"] = self.description
        if self.properties is not None:
            result["properties"] = self.properties
        return result


@dataclass
class MethodError:
    """Top‑level method‑call error returned as an ``error`` method response.

    Attributes:
        type: Machine‑readable error identifier (e.g. ``unknownMethod``).
        description: Human‑readable description, may be ``None``.
    """

    type: str
    description: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> MethodError:
        """Create a :class:`MethodError` from its JSON representation."""
        return cls(
            type=data["type"],
            description=data.get("description"),
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the instance to a JSON‑compatible ``dict``."""
        result: Dict[str, Any] = {"type": self.type}
        if self.description is not None:
            result["description"] = self.description
        return result


@dataclass
class ResultReference:
    """Back‑reference used inside a request argument to point at a value produced by an earlier method call.

    Attributes:
        result_of: Identifier of the earlier method call.
        name: Name of the result property to reference.
        path: JSON Pointer into the referenced result.
    """

    result_of: str
    name: str
    path: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> ResultReference:
        """Create a :class:`ResultReference` from its JSON representation."""
        return cls(
            result_of=data["resultOf"],
            name=data["name"],
            path=data["path"],
        )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the instance to a JSON‑compatible ``dict``."""
        return {
            "resultOf": self.result_of,
            "name": self.name,
            "path": self.path,
        }


# ----------------------------------------------------------------------
# Exception hierarchy
# ----------------------------------------------------------------------


class JmapError(Exception):
    """Base class for all JMAP‑related exceptions."""


class JmapProtocolError(JmapError):
    """Raised when the JMAP server returns an error response.

    Attributes:
        type: Machine‑readable error identifier from the server.
        description: Optional human‑readable description.
    """

    def __init__(self, type: str, description: Optional[str] = None) -> None:
        self.type = type
        self.description = description
        message = f"JMAP protocol error [{type}]"
        if description:
            message += f": {description}"
        super().__init__(message)


class JmapNetworkError(JmapError):
    """Raised when a transport‑level/network failure occurs.

    Attributes:
        original_exception: The underlying exception that triggered the failure.
    """

    def __init__(self, original_exception: Exception) -> None:
        self.original_exception = original_exception
        super().__init__(f"JMAP network error: {original_exception}")  # pragma: no cover


__all__ = [
    "SetError",
    "MethodError",
    "ResultReference",
    "JmapError",
    "JmapProtocolError",
    "JmapNetworkError",
]
