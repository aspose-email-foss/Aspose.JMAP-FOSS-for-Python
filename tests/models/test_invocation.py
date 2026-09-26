"""Tests for the public :class:`Invocation` model."""

from __future__ import annotations

import pytest

# Import the model directly to avoid pulling in the package's top‑level
# re‑exports, which may import unrelated buggy modules.
from aspose_jmap_foss.models.invocation import Invocation


def test_invocation_to_json_produces_correct_list() -> None:
    """Normal case: ``to_json`` returns the exact JMAP array representation."""
    inv = Invocation(
        name="Email/get",
        arguments={
            "accountId": "user-123",
            "ids": ["m1", "m2"],
            "properties": ["subject", "from"],
        },
        method_call_id="c1",
    )
    expected = [
        "Email/get",
        {
            "accountId": "user-123",
            "ids": ["m1", "m2"],
            "properties": ["subject", "from"],
        },
        "c1",
    ]
    assert inv.to_json() == expected


def test_invocation_from_json_round_trip() -> None:
    """Round‑trip ``from_json`` → ``to_json`` yields an equivalent object."""
    payload = [
        "Mailbox/get",
        {"accountId": "acct-1", "ids": []},
        "mid-42",
    ]
    inv = Invocation.from_json(payload)
    assert inv.name == "Mailbox/get"
    assert inv.arguments == {"accountId": "acct-1", "ids": []}
    assert inv.method_call_id == "mid-42"
    # Serialising back must give the original list.
    assert inv.to_json() == payload
    # Equality defined by dataclass should hold.
    assert inv == Invocation(
        name="Mailbox/get",
        arguments={"accountId": "acct-1", "ids": []},
        method_call_id="mid-42",
    )


def test_invocation_from_json_invalid_input_raises() -> None:
    """Edge case: non‑list or wrong‑length input raises ``ValueError``."""
    with pytest.raises(ValueError):
        # Wrong type (dict instead of list)
        Invocation.from_json(
            {"name": "Email/get", "arguments": {}, "methodCallId": "c2"}  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError):
        # List with incorrect length
        Invocation.from_json(["only", "two"])  # type: ignore[arg-type]
