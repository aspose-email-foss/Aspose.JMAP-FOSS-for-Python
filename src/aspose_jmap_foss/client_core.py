"""Core client mixin for Aspose.JMAP FOSS.

Provides session handling, generic request sending, and wrappers for the Core
JMAP methods and the upload/download blob endpoints.
"""

from __future__ import annotations

import base64
import json
import uuid
from urllib.parse import quote, urljoin
from dataclasses import dataclass, field
from typing import Any, List, Tuple, Optional

from .models.invocation import Invocation
from .models.common_types import JmapError, JmapNetworkError, JmapProtocolError
from .models.jmap_request_envelope import JmapRequestEnvelope
from .models.jmap_response_envelope import JmapResponseEnvelope
from .models.transport import JmapTransport, UrllibJmapTransport, JmapHttpRequest, JmapHttpResponse
from .models.session import Session


CORE_CAPABILITY = "urn:ietf:params:jmap:core"


def _basic_auth_header(username: str, password: str) -> str:
    token = f"{username}:{password}".encode("utf-8")
    return "Basic " + base64.b64encode(token).decode("ascii")


def _build_auth_header(options: "JmapClientOptions") -> str:
    """Compute the ``Authorization`` header value for the given options.

    If ``bearer_token`` is set (non-``None`` and non-empty), an RFC 6750
    Bearer token header is used. Otherwise this falls back to HTTP Basic
    authentication derived from ``username``/``password``.
    """
    if options.bearer_token:
        return "Bearer " + options.bearer_token
    return _basic_auth_header(options.username, options.password)


@dataclass
class JmapClientOptions:
    """Configuration for :class:`JmapClient`.

    Attributes
    ----------
    session_url:
        URL of the JMAP session resource (e.g. ``https://example/.well-known/jmap``).
    username:
        Username for HTTP Basic authentication.
    password:
        Password for HTTP Basic authentication.
    bearer_token:
        Optional OAuth 2.0 bearer token (RFC 6750). When set (non-empty), it takes
        precedence over ``username``/``password`` and the client authenticates
        using ``Authorization: Bearer <bearer_token>`` instead of HTTP Basic auth.
    transport:
        Optional custom transport implementing :class:`JmapTransport`. If omitted,
        :class:`UrllibJmapTransport` is used.
    """

    session_url: str
    username: str
    password: str
    bearer_token: Optional[str] = None
    transport: Optional[JmapTransport] = None


class _CoreClientMixin:
    """Mixin that implements core JMAP client behaviour.

    The final public client class is composed from this mixin together with
    other module‑specific mixins.
    """

    def __init__(self, options: JmapClientOptions) -> None:
        self._options: JmapClientOptions = options
        self._transport: JmapTransport = (
            options.transport if options.transport is not None else UrllibJmapTransport()
        )
        self._session: Optional[Session] = None
        self._auth_header: str = _build_auth_header(options)

    # --------------------------------------------------------------------- #
    # Context‑manager protocol
    # --------------------------------------------------------------------- #
    def __enter__(self) -> "_CoreClientMixin":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        """Dispose of client resources.

        The default transport does not require explicit cleanup, so this is a
        no‑op placeholder for future extensions.
        """
        # No explicit cleanup required for the built‑in transport.
        return None

    # --------------------------------------------------------------------- #
    # Session handling
    # --------------------------------------------------------------------- #
    def connect(self) -> Session:
        """Fetch the JMAP session object and store it for later calls.

        Returns
        -------
        Session
            The parsed session information.

        Raises
        ------
        JmapNetworkError
            If the underlying transport cannot retrieve the session.
        JmapProtocolError
            If the response cannot be parsed as a valid session object.
        """
        request = JmapHttpRequest(
            method="GET",
            url=self._options.session_url,
            headers={"Authorization": self._auth_header},
        )
        response: JmapHttpResponse = self._transport.send(request)
        try:
            data = json.loads(response.body)
        except json.JSONDecodeError as exc:
            raise JmapProtocolError("invalidJson", "Session response is not valid JSON") from exc

        session = Session.from_json(data)
        # apiUrl/downloadUrl/uploadUrl/eventSourceUrl may be relative (per RFC 8620); resolve
        # them against the session URL's origin (real servers, e.g. Stalwart, send relative URLs).
        session.api_url = urljoin(self._options.session_url, session.api_url)
        session.download_url = urljoin(self._options.session_url, session.download_url)
        session.upload_url = urljoin(self._options.session_url, session.upload_url)
        session.event_source_url = urljoin(self._options.session_url, session.event_source_url)
        self._session = session
        return self._session

    # --------------------------------------------------------------------- #
    # Low‑level request helper
    # --------------------------------------------------------------------- #
    def send_request(
        self,
        method_calls: List[Tuple[str, dict, str]] | List[Invocation],
        using: List[str],
    ) -> JmapResponseEnvelope:
        """Send a JMAP request envelope and return the parsed response.

        Public so callers can batch multiple method calls into a single HTTP
        round trip (RFC 8620 section 3.7): pass more than one entry in
        ``method_calls``, and use a :class:`~.models.common_types.ResultReference`
        as a later call's argument value (under a key prefixed with ``#``, e.g.
        ``{"#ids": ResultReference(result_of="c1", name="Email/query", path="/ids").to_json()}``
        - call ``.to_json()`` on it since ``Invocation.arguments`` values must
        already be JSON-compatible) to reference an earlier call's response
        without a second request.

        Parameters
        ----------
        method_calls
            List of method call specifications. Each element may be a
            ``(name, arguments, call_id)`` tuple or an :class:`Invocation`.
        using
            List of capability URNs required for the request.

        Returns
        -------
        JmapResponseEnvelope
            Parsed response envelope.

        Raises
        ------
        JmapNetworkError
            Propagated from the transport on low‑level failures.
        JmapProtocolError
            If any method response entry has the name ``"error"``.
        """
        if self._session is None:
            raise JmapProtocolError("sessionMissing", "Client must call connect() first")

        # Normalise to Invocation objects
        invocations: List[Invocation] = []
        for item in method_calls:
            if isinstance(item, Invocation):
                invocations.append(item)
            else:
                name, arguments, call_id = item
                invocations.append(Invocation(name=name, arguments=arguments, method_call_id=call_id))

        envelope = JmapRequestEnvelope(using=using, method_calls=invocations)
        body_bytes = json.dumps(envelope.to_json()).encode("utf-8")

        http_req = JmapHttpRequest(
            method="POST",
            url=self._session.api_url,
            headers={
                "Authorization": self._auth_header,
                "Content-Type": "application/json",
            },
            body=body_bytes,
        )
        http_resp = self._transport.send(http_req)

        try:
            resp_data = json.loads(http_resp.body)
        except json.JSONDecodeError as exc:
            raise JmapProtocolError("invalidJson", "Response body is not valid JSON") from exc

        resp_envelope = JmapResponseEnvelope.from_json(resp_data)

        # Detect protocol‑level errors
        for inv in resp_envelope.method_responses:
            if inv.name == "error":
                err_type = inv.arguments.get("type", "unknown")
                description = inv.arguments.get("description", "")
                raise JmapProtocolError(err_type, description)

        return resp_envelope

    # --------------------------------------------------------------------- #
    # Core method wrappers
    # --------------------------------------------------------------------- #
    def echo(self, account_id: str, arguments: dict) -> dict:
        """Call the Core/echo method.

        Parameters
        ----------
        account_id
            The account identifier to include in the request.
        arguments
            Arbitrary JSON‑compatible object that will be echoed back.

        Returns
        -------
        dict
            The echoed arguments object.

        Raises
        ------
        JmapProtocolError
            If the server returns an error response.
        """
        invocation = Invocation(name="Core/echo", arguments=arguments, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[CORE_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", "No matching response for echo call")
        return resp_env.method_responses[0].arguments

    # --------------------------------------------------------------------- #
    # Blob upload / download
    # --------------------------------------------------------------------- #
    def upload_blob(self, account_id: str, data: bytes, content_type: str) -> dict:
        """Upload a binary blob to the server.

        Parameters
        ----------
        account_id
            Account identifier to expand in the upload URL.
        data
            Raw bytes to upload.
        content_type
            MIME type of the blob.

        Returns
        -------
        dict
            Parsed JSON response containing ``accountId``, ``blobId``, ``type``,
            and ``size`` fields.

        Raises
        ------
        JmapProtocolError
            If the response cannot be parsed.
        """
        if self._session is None:
            raise JmapProtocolError("sessionMissing", "Client must call connect() first")
        # Percent-encode: account_id is substituted verbatim into a URL path segment, and
        # `/`, `?`, `#`, etc. in it would otherwise rewrite the request path or smuggle
        # extra query parameters into the upload URL.
        upload_url = self._session.upload_url.format(accountId=quote(account_id, safe=""))

        http_req = JmapHttpRequest(
            method="POST",
            url=upload_url,
            headers={
                "Authorization": self._auth_header,
                "Content-Type": content_type,
            },
            body=data,
        )
        http_resp = self._transport.send(http_req)

        try:
            return json.loads(http_resp.body)
        except json.JSONDecodeError as exc:
            raise JmapProtocolError("invalidJson", "Upload response is not valid JSON") from exc

    def download_blob(
        self,
        account_id: str,
        blob_id: str,
        type_: str,
        name: Optional[str] = None,
    ) -> bytes:
        """Download a previously uploaded blob.

        Parameters
        ----------
        account_id
            Account identifier to expand in the download URL.
        blob_id
            Identifier of the blob to retrieve.
        type_
            MIME type placeholder for the URL.
        name
            Optional filename placeholder for the URL.

        Returns
        -------
        bytes
            Raw blob content.

        Raises
        ------
        JmapProtocolError
            If the response cannot be retrieved.
        """
        if self._session is None:
            raise JmapProtocolError("sessionMissing", "Client must call connect() first")
        # Percent-encode each substituted value: they are spliced verbatim into a URL path
        # segment, and `/`, `?`, `#`, etc. in any of them would otherwise rewrite the
        # request path or smuggle extra query parameters into the download URL.
        url_template = self._session.download_url
        url = url_template.format(
            accountId=quote(account_id, safe=""),
            blobId=quote(blob_id, safe=""),
            type=quote(type_, safe=""),
            name=quote(name, safe="") if name else "",
        )
        http_req = JmapHttpRequest(
            method="GET",
            url=url,
            headers={"Authorization": self._auth_header},
        )
        http_resp = self._transport.send(http_req)
        return http_resp.body
