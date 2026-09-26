"""Mail client mixin for Aspose.JMAP FOSS.

Provides convenience methods for the JMAP Mail module. Each method sends a
single JMAP method call using a fixed call identifier ``"c1"`` and the
``urn:ietf:params:jmap:mail`` capability.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models.comparator import Comparator
from .models.email import Email
from .models.email_query_response import EmailQueryResponse
from .models.identity import Identity
from .models.mailbox import Mailbox
from .models.search_snippet import SearchSnippet
from .models.thread import Thread
from .models.common_types import JmapProtocolError
from .models.invocation import Invocation

MAIL_CAPABILITY = "urn:ietf:params:jmap:mail"


class _MailClientMixin:
    """Mixin adding Mail‑module methods to :class:`JmapClient`."""

    # --------------------------------------------------------------------- #
    # Mailbox helpers
    # --------------------------------------------------------------------- #
    def list_mailboxes(self, account_id: str) -> List[Mailbox]:
        """Return all mailboxes for ``account_id``."""
        args: Dict[str, Any] = {"accountId": account_id}
        invocation = Invocation(name="Mailbox/get", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        mailboxes_json = resp.arguments.get("list", [])
        return [Mailbox.from_json(m) for m in mailboxes_json]

    def get_mailbox(
        self,
        account_id: str,
        ids: Optional[List[str]] = None,
        properties: Optional[List[str]] = None,
    ) -> List[Mailbox]:
        """Retrieve specific mailboxes."""
        args: Dict[str, Any] = {"accountId": account_id}
        if ids is not None:
            args["ids"] = ids
        if properties is not None:
            args["properties"] = properties
        invocation = Invocation(name="Mailbox/get", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        return [Mailbox.from_json(m) for m in resp.arguments.get("list", [])]

    def create_mailbox(
        self,
        account_id: str,
        create: Dict[str, Mailbox],
    ) -> Dict[str, Mailbox]:
        """Create one or more mailboxes.

        ``create`` maps client‑chosen ids to :class:`Mailbox` instances.
        """
        args: Dict[str, Any] = {
            "accountId": account_id,
            "create": {k: v.to_json() for k, v in create.items()},
        }
        invocation = Invocation(name="Mailbox/set", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        created_json = resp.arguments.get("created", {})
        # Per RFC 8620 5.3, a "created" entry only includes server-assigned/defaulted
        # properties the client didn't already send - merge it onto what was sent.
        result: Dict[str, Mailbox] = {}
        for k, server_json in created_json.items():
            merged = {**create[k].to_json(), **server_json}
            result[k] = Mailbox.from_json(merged)
        return result

    def delete_mailbox(self, account_id: str, destroy: List[str]) -> List[str]:
        """Delete the specified mailboxes."""
        args: Dict[str, Any] = {"accountId": account_id, "destroy": destroy}
        invocation = Invocation(name="Mailbox/set", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        return resp.arguments.get("destroyed", [])

    # --------------------------------------------------------------------- #
    # Message helpers
    # --------------------------------------------------------------------- #
    def list_messages(
        self,
        account_id: str,
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Comparator]] = None,
        limit: Optional[int] = None,
        position: int = 0,
    ) -> EmailQueryResponse:
        """Return the full Email/query result matching the optional filter.

        Returns:
            An :class:`EmailQueryResponse` containing the matching message
            ids together with the query state, paging and total-count
            metadata returned by the server (RFC 8620 section 5.5).
        """
        args: Dict[str, Any] = {"accountId": account_id, "position": position}
        if filter is not None:
            args["filter"] = filter
        if sort is not None:
            args["sort"] = [c.to_json() for c in sort]
        if limit is not None:
            args["limit"] = limit
        invocation = Invocation(name="Email/query", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        return EmailQueryResponse.from_json(resp.arguments)

    def fetch_message(
        self,
        account_id: str,
        ids: List[str],
        properties: Optional[List[str]] = None,
        body_properties: Optional[List[str]] = None,
        fetch_text_body_values: bool = False,
        fetch_html_body_values: bool = False,
        fetch_all_body_values: bool = False,
        max_body_value_bytes: Optional[int] = None,
    ) -> List[Email]:
        """Retrieve full ``Email`` objects for the given ids."""
        args: Dict[str, Any] = {
            "accountId": account_id,
            "ids": ids,
            "fetchTextBodyValues": fetch_text_body_values,
            "fetchHTMLBodyValues": fetch_html_body_values,
            "fetchAllBodyValues": fetch_all_body_values,
        }
        if properties is not None:
            args["properties"] = properties
        if body_properties is not None:
            args["bodyProperties"] = body_properties
        if max_body_value_bytes is not None:
            args["maxBodyValueBytes"] = max_body_value_bytes

        invocation = Invocation(name="Email/get", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        return [Email.from_json(e) for e in resp.arguments.get("list", [])]

    def move_message(
        self,
        account_id: str,
        email_id: str,
        to_mailbox_id: str,
    ) -> Optional[Email]:
        """Move a message to another mailbox."""
        args: Dict[str, Any] = {
            "accountId": account_id,
            "update": {
                email_id: {"mailboxIds": {to_mailbox_id: True}},
            },
        }
        invocation = Invocation(name="Email/set", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        updated = resp.arguments.get("updated", {})
        if email_id in updated and updated[email_id] is not None:
            return Email.from_json(updated[email_id])
        return None

    def set_message_keyword(
        self,
        account_id: str,
        email_id: str,
        keyword: str,
        value: bool,
    ) -> Optional[Email]:
        """Set or clear a keyword on a message."""
        args: Dict[str, Any] = {
            "accountId": account_id,
            "update": {
                email_id: {"keywords": {keyword: value}},
            },
        }
        invocation = Invocation(name="Email/set", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        updated = resp.arguments.get("updated", {})
        if email_id in updated and updated[email_id] is not None:
            return Email.from_json(updated[email_id])
        return None

    def delete_message(self, account_id: str, destroy: List[str]) -> List[str]:
        """Delete the specified messages."""
        args: Dict[str, Any] = {"accountId": account_id, "destroy": destroy}
        invocation = Invocation(name="Email/set", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        return resp.arguments.get("destroyed", [])

    # --------------------------------------------------------------------- #
    # Identity helpers
    # --------------------------------------------------------------------- #
    def list_identities(
        self,
        account_id: str,
        ids: Optional[List[str]] = None,
        properties: Optional[List[str]] = None,
    ) -> List[Identity]:
        """Return identities for the given account."""
        args: Dict[str, Any] = {"accountId": account_id}
        if ids is not None:
            args["ids"] = ids
        if properties is not None:
            args["properties"] = properties
        invocation = Invocation(name="Identity/get", arguments=args, method_call_id="c1")
        resp_env = self.send_request([invocation], using=[MAIL_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        resp = resp_env.method_responses[0]
        return [Identity.from_json(i) for i in resp.arguments.get("list", [])]
