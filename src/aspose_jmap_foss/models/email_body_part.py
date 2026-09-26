from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .email_header import EmailHeader


@dataclass
class EmailBodyPart:
    """One node of the Email's MIME bodyStructure tree."""

    # Required fields (no defaults)
    size: int = field(metadata={"json_name": "size"})
    type: str = field(metadata={"json_name": "type"})
    headers: List[EmailHeader] = field(metadata={"json_name": "headers"})

    # Optional fields (defaults)
    part_id: Optional[str] = field(
        default=None, metadata={"json_name": "partId"}
    )
    blob_id: Optional[str] = field(
        default=None, metadata={"json_name": "blobId"}
    )
    name: Optional[str] = field(
        default=None, metadata={"json_name": "name"}
    )
    charset: Optional[str] = field(
        default=None, metadata={"json_name": "charset"}
    )
    disposition: Optional[str] = field(
        default=None, metadata={"json_name": "disposition"}
    )
    cid: Optional[str] = field(
        default=None, metadata={"json_name": "cid"}
    )
    language: Optional[List[str]] = field(
        default=None, metadata={"json_name": "language"}
    )
    location: Optional[str] = field(
        default=None, metadata={"json_name": "location"}
    )
    sub_parts: Optional[List[EmailBodyPart]] = field(
        default=None, metadata={"json_name": "subParts"}
    )

    @classmethod
    def from_json(cls, data: dict) -> EmailBodyPart:
        """Create an EmailBodyPart instance from its JMAP JSON representation."""
        return cls(
            size=data["size"],
            type=data["type"],
            headers=[EmailHeader.from_json(h) for h in data["headers"]],
            part_id=data.get("partId"),
            blob_id=data.get("blobId"),
            name=data.get("name"),
            charset=data.get("charset"),
            disposition=data.get("disposition"),
            cid=data.get("cid"),
            language=data.get("language"),
            location=data.get("location"),
            sub_parts=(
                [EmailBodyPart.from_json(sp) for sp in data["subParts"]]
                if data.get("subParts") is not None
                else None
            ),
        )

    def to_json(self) -> dict:
        """Serialize the EmailBodyPart instance to its JMAP JSON representation."""
        result: dict = {
            "size": self.size,
            "type": self.type,
            "headers": [h.to_json() for h in self.headers],
            "partId": self.part_id,
            "blobId": self.blob_id,
            "name": self.name,
            "charset": self.charset,
            "disposition": self.disposition,
            "cid": self.cid,
            "language": self.language,
            "location": self.location,
            "subParts": (
                [sp.to_json() for sp in self.sub_parts]
                if self.sub_parts is not None
                else None
            ),
        }
        return result
