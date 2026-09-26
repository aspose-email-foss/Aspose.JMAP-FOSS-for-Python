from __future__ import annotations

import pytest

from aspose_jmap_foss.models.email_body_part import EmailBodyPart
from aspose_jmap_foss.models.email_header import EmailHeader


def test_email_body_part_full_roundtrip() -> None:
    """Serialize and deserialize a fully populated EmailBodyPart."""
    json_data = {
        "size": 1234,
        "type": "multipart/alternative",
        "headers": [
            {"name": "Content-Type", "value": "multipart/alternative"},
            {"name": "Subject", "value": "Test email"},
        ],
        "partId": "0",
        "blobId": "blob123",
        "name": "example.eml",
        "charset": "utf-8",
        "disposition": "attachment",
        "cid": "<cid@example.com>",
        "language": ["en", "fr"],
        "location": "us-east",
        "subParts": [
            {
                "size": 567,
                "type": "text/plain",
                "headers": [{"name": "Content-Type", "value": "text/plain"}],
                "partId": "0.1",
                "blobId": "blob456",
                "name": None,
                "charset": "utf-8",
                "disposition": None,
                "cid": None,
                "language": None,
                "location": None,
                "subParts": None,
            }
        ],
    }

    # Deserialize
    part = EmailBodyPart.from_json(json_data)

    # Verify top‑level fields
    assert part.size == 1234
    assert part.type == "multipart/alternative"
    assert part.part_id == "0"
    assert part.blob_id == "blob123"
    assert part.name == "example.eml"
    assert part.charset == "utf-8"
    assert part.disposition == "attachment"
    assert part.cid == "<cid@example.com>"
    assert part.language == ["en", "fr"]
    assert part.location == "us-east"
    assert part.headers == [
        EmailHeader(name="Content-Type", value="multipart/alternative"),
        EmailHeader(name="Subject", value="Test email"),
    ]

    # Verify nested sub‑part
    assert part.sub_parts is not None
    sub = part.sub_parts[0]
    assert sub.size == 567
    assert sub.type == "text/plain"
    assert sub.part_id == "0.1"
    assert sub.blob_id == "blob456"
    assert sub.headers == [EmailHeader(name="Content-Type", value="text/plain")]
    assert sub.name is None
    assert sub.charset == "utf-8"
    assert sub.disposition is None
    assert sub.cid is None
    assert sub.language is None
    assert sub.location is None
    assert sub.sub_parts is None

    # Serialize back to JSON and compare (order of keys is not significant)
    assert part.to_json() == json_data


def test_email_body_part_minimal_fields() -> None:
    """Deserialize with only required fields and ensure optional ones are None."""
    json_data = {
        "size": 42,
        "type": "text/plain",
        "headers": [{"name": "Content-Type", "value": "text/plain"}],
    }

    part = EmailBodyPart.from_json(json_data)

    # Required fields
    assert part.size == 42
    assert part.type == "text/plain"
    assert part.headers == [EmailHeader(name="Content-Type", value="text/plain")]

    # Optional fields should be None
    assert part.part_id is None
    assert part.blob_id is None
    assert part.name is None
    assert part.charset is None
    assert part.disposition is None
    assert part.cid is None
    assert part.language is None
    assert part.location is None
    assert part.sub_parts is None

    # to_json must still emit all keys, with None for omitted optionals
    expected_json = {
        "size": 42,
        "type": "text/plain",
        "headers": [{"name": "Content-Type", "value": "text/plain"}],
        "partId": None,
        "blobId": None,
        "name": None,
        "charset": None,
        "disposition": None,
        "cid": None,
        "language": None,
        "location": None,
        "subParts": None,
    }
    assert part.to_json() == expected_json
