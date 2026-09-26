"""Submission client mixin for Aspose.JMAP FOSS.

Provides convenience methods for the ``EmailSubmission`` JMAP methods.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models.comparator import Comparator
from .models.email_submission import EmailSubmission
from .models.common_types import JmapProtocolError, SetError
from .models.invocation import Invocation
from .models.jmap_response_envelope import JmapResponseEnvelope

SUBMISSION_CAPABILITY = "urn:ietf:params:jmap:submission"


class _SubmissionClientMixin:
    """Mixin that implements the ``submission`` module API.

    Assumes the core mixin has already set up ``self.send_request`` and
    ``self._session``.
    """

    def send(
        self,
        account_id: str,
        create: Optional[Dict[str, EmailSubmission]] = None,
        on_success_update_email: Optional[Dict[str, Dict[str, Any]]] = None,
        on_success_destroy_email: Optional[List[str]] = None,
        if_in_state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create one or more ``EmailSubmission`` objects (i.e. send emails).

        Parameters
        ----------
        account_id
            Identifier of the account on which to perform the operation.
        create
            Mapping from client‑chosen creation IDs to :class:`EmailSubmission`
            instances describing the messages to send.
        on_success_update_email
            Optional map of creation IDs to patch objects applied to the
            underlying ``Email`` objects when the submission succeeds.
        on_success_destroy_email
            Optional list of creation IDs whose underlying ``Email`` objects
            should be destroyed when the submission succeeds.
        if_in_state
            Optional state token to require for conditional updates.

        Returns
        -------
        dict
            The raw method‑response arguments from the server, containing keys
            such as ``created``, ``oldState``, ``newState`` and any per‑id
            ``notCreated`` errors.
        """
        args: Dict[str, Any] = {"accountId": account_id}
        if if_in_state is not None:
            args["ifInState"] = if_in_state
        if create is not None:
            args["create"] = {cid: sub.to_json() for cid, sub in create.items()}
        if on_success_update_email is not None:
            args["onSuccessUpdateEmail"] = on_success_update_email
        if on_success_destroy_email is not None:
            args["onSuccessDestroyEmail"] = on_success_destroy_email

        invocation = Invocation(
            name="EmailSubmission/set",
            arguments=args,
            method_call_id="c1",
        )
        resp_env: JmapResponseEnvelope = self.send_request([invocation], using=[SUBMISSION_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        return resp_env.method_responses[0].arguments

    def cancel_send(
        self,
        account_id: str,
        update: Optional[Dict[str, Dict[str, Any]]] = None,
        if_in_state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cancel a previously created ``EmailSubmission`` (set ``undoStatus``).

        Parameters
        ----------
        account_id
            Identifier of the account on which to perform the operation.
        update
            Mapping from ``EmailSubmission`` IDs to patch objects.  Typically
            ``{\"undoStatus\": \"canceled\"}`` (a PatchObject key is a JSON Pointer
            *relative to the object being patched*, e.g. RFC 6901 - a bare top-level
            property name like ``undoStatus`` has no leading ``/``; that would instead
            point at a property literally named the empty string).
        if_in_state
            Optional state token to require for conditional updates.

        Returns
        -------
        dict
            The raw method‑response arguments from the server, containing keys
            such as ``updated`` and any per‑id ``notUpdated`` errors.
        """
        args: Dict[str, Any] = {"accountId": account_id}
        if if_in_state is not None:
            args["ifInState"] = if_in_state
        if update is not None:
            args["update"] = update

        invocation = Invocation(
            name="EmailSubmission/set",
            arguments=args,
            method_call_id="c1",
        )
        resp_env: JmapResponseEnvelope = self.send_request([invocation], using=[SUBMISSION_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        return resp_env.method_responses[0].arguments

    def list_submissions(
        self,
        account_id: str,
        ids: Optional[List[str]] = None,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Retrieve ``EmailSubmission`` objects.

        Parameters
        ----------
        account_id
            Identifier of the account on which to perform the operation.
        ids
            Optional list of ``EmailSubmission`` IDs to retrieve.  If omitted,
            all submissions are returned.
        properties
            Optional list of property names to include in each returned object.

        Returns
        -------
        dict
            The raw method‑response arguments from the server, containing keys
            ``list``, ``state`` and any ``notFound`` IDs.
        """
        args: Dict[str, Any] = {"accountId": account_id}
        if ids is not None:
            args["ids"] = ids
        if properties is not None:
            args["properties"] = properties

        invocation = Invocation(
            name="EmailSubmission/get",
            arguments=args,
            method_call_id="c1",
        )
        resp_env: JmapResponseEnvelope = self.send_request([invocation], using=[SUBMISSION_CAPABILITY])
        if not resp_env.method_responses:
            raise JmapProtocolError("missingResponse", f"No matching response for {invocation.name} call")
        return resp_env.method_responses[0].arguments
