"""Transport seam for JMAP client.

Defines the abstract transport interface, low‑level request/response value
objects, and the default urllib‑based implementation.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional
from urllib.parse import urlsplit

from .common_types import JmapError, JmapNetworkError, JmapProtocolError

_CREDENTIAL_HEADERS = ("authorization", "cookie", "proxy-authorization")


def _origin(url: str) -> tuple[str, str, int]:
    parts = urlsplit(url)
    return (parts.scheme, parts.hostname or "", parts.port or -1)


class _CrossOriginSafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follows redirects like the stdlib handler, but strips the caller's credentials
    (``Authorization`` / ``Cookie`` / ``Proxy-Authorization``) when the redirect target's
    origin differs from the original request's - stdlib ``urllib`` forwards them to any host
    on Python <= 3.12, which would leak a bearer token / Basic credentials to a hostile
    redirect target. Same-origin redirects keep every header.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req is not None and _origin(newurl) != _origin(req.full_url):
            for name in list(new_req.headers):
                if name.lower() in _CREDENTIAL_HEADERS:
                    del new_req.headers[name]
            for name in list(getattr(new_req, "unredirected_hdrs", {})):
                if name.lower() in _CREDENTIAL_HEADERS:
                    del new_req.unredirected_hdrs[name]
        return new_req


@dataclass
class JmapHttpRequest:
    """Low‑level HTTP request used by the JMAP client.

    Attributes:
        method: HTTP method (e.g. ``"POST"``).
        url: Full request URL.
        headers: Mapping of header names to values.
        body: Optional raw request body bytes (JSON-method-call bodies are UTF-8-encoded
            JSON text; blob uploads are the blob's raw bytes verbatim). Deliberately bytes,
            not str: a str body would force every caller - including blob uploads, which are
            not text - through a lossy UTF-8 encode/decode round-trip.
    """

    method: str
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)
    body: Optional[bytes] = None


@dataclass
class JmapHttpResponse:
    """Low‑level HTTP response returned by a transport.

    Attributes:
        status_code: HTTP status code (e.g. ``200``).
        headers: Mapping of response header names to values.
        body: Raw response body bytes (typically JSON text, but a blob download's body is
            arbitrary binary data - see the note on :class:`JmapHttpRequest`.body).
    """

    status_code: int
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes = b""


class JmapTransport(ABC):
    """Abstract base class for JMAP transports.

    Implementations must provide :meth:`send` which takes a
    :class:`JmapHttpRequest` and returns a :class:`JmapHttpResponse`.
    """

    @abstractmethod
    def send(self, request: JmapHttpRequest) -> JmapHttpResponse:
        """Send *request* and return the corresponding response.

        Raises:
            JmapNetworkError: If a low‑level network or transport error occurs.
        """
        raise NotImplementedError


class UrllibJmapTransport(JmapTransport):
    """Default transport implementation using :mod:`urllib.request`.

    This class performs a synchronous HTTP request using the standard library.
    """

    def __init__(self, timeout: float = 30.0) -> None:
        """Create a transport.

        Args:
            timeout: Seconds to wait for a response before raising an error.
        """
        self._timeout = timeout
        # A private opener so redirect handling is our cross-origin-safe one, not the
        # process-global default (which forwards Authorization to any host).
        self._opener = urllib.request.build_opener(_CrossOriginSafeRedirectHandler())

    def send(self, request: JmapHttpRequest) -> JmapHttpResponse:
        """Send *request* via ``urllib`` and return a :class:`JmapHttpResponse`.

        Args:
            request: The low‑level request to perform.

        Returns:
            A response object containing status, headers and body.

        Raises:
            JmapNetworkError: If the request cannot be completed due to a
                network‑level problem.
        """
        urllib_req = urllib.request.Request(
            url=request.url,
            data=request.body,
            headers=dict(request.headers),
            method=request.method,
        )

        try:
            with self._opener.open(urllib_req, timeout=self._timeout) as resp:
                status = resp.getcode()
                resp_headers = dict(resp.info())
                resp_body_bytes = resp.read()
                return JmapHttpResponse(
                    status_code=status,
                    headers=resp_headers,
                    body=resp_body_bytes,
                )
        except urllib.error.URLError as exc:
            # URLError includes HTTPError (non‑2xx) as a subclass; treat it as a
            # network failure for the purposes of this transport.
            raise JmapNetworkError(exc) from exc


__all__ = [
    "JmapHttpRequest",
    "JmapHttpResponse",
    "JmapTransport",
    "UrllibJmapTransport",
    "JmapError",
    "JmapProtocolError",
    "JmapNetworkError",
]
