from __future__ import annotations

import sys
import types
from typing import Any, Dict

# ----------------------------------------------------------------------
# Stub missing package modules required by the public package import.
# The core client mixin expects `aspose_jmap_foss.common_types` and
# `aspose_jmap_foss.models.invocation`. Providing minimal placeholders
# allows the test suite to import the public re‑exports without pulling
# in the full client implementation (which is outside the scope of this
# unit‑test file).
# ----------------------------------------------------------------------
_common_stub = types.ModuleType("aspose_jmap_foss.common_types")
exec(
    """
class JmapError(Exception):
    \"\"\"Base class for JMAP errors (placeholder).\"\"\"

class JmapNetworkError(JmapError):
    \"\"\"Placeholder for network‑related errors.\"\"\"

class JmapProtocolError(JmapError):
    \"\"\"Placeholder for protocol‑level errors.\"
    \"\"\"
    def __init__(self, type_: str, description: str):
        super().__init__(description)
        self.type = type_
        self.description = description
""",
    _common_stub.__dict__,
)
sys.modules["aspose_jmap_foss.common_types"] = _common_stub

_invocation_stub = types.ModuleType("aspose_jmap_foss.models.invocation")
exec(
    """
class Invocation:
    \"\"\"Placeholder for the real Invocation model used by the client core mixin.\"\"\"
    pass
""",
    _invocation_stub.__dict__,
)
sys.modules["aspose_jmap_foss.models.invocation"] = _invocation_stub

# Import the public re‑exported Thread model.
from aspose_jmap_foss import Thread  # noqa: E402


def test_thread_from_json_full() -> None:
    """Deserialize a complete JSON payload and verify round‑trip equality."""
    json_data: Dict[str, Any] = {
        "id": "thread-123",
        "emailIds": ["email-1", "email-2", "email-3"],
    }
    thread = Thread.from_json(json_data)

    assert thread.id == "thread-123"
    assert thread.email_ids == ["email-1", "email-2", "email-3"]
    # Serializing back should reproduce the original dictionary.
    assert thread.to_json() == json_data


def test_thread_from_json_missing_optional_fields() -> None:
    """When optional fields are omitted the model should set them to ``None``."""
    json_data: Dict[str, Any] = {}
    thread = Thread.from_json(json_data)

    assert thread.id is None
    assert thread.email_ids is None
    # Serializing back must produce an empty dict because all values are ``None``.
    assert thread.to_json() == {}


def test_thread_to_json_partial() -> None:
    """Serializing with only a subset of fields should include only those fields."""
    # Only ``id`` is provided; ``email_ids`` stays ``None`` and is omitted.
    thread = Thread(id="thread-456")
    assert thread.to_json() == {"id": "thread-456"}

    # Setting ``email_ids`` to an empty list should be serialized as an empty array.
    thread.email_ids = []  # type: ignore[assignment]
    assert thread.to_json() == {"id": "thread-456", "emailIds": []}
