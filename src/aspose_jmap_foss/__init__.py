# Auto-generated composition file (template-rendered, not an LLM task).
# Wires together the per-module client mixins produced by the codegen pipeline.
from __future__ import annotations

from .client_core import _CoreClientMixin, JmapClientOptions
from .models.common_types import SetError, MethodError, ResultReference, JmapError, JmapProtocolError, JmapNetworkError
from .models.transport import JmapTransport, UrllibJmapTransport, JmapHttpRequest, JmapHttpResponse
from .models.session import Session, Account, CoreCapability
from .models.invocation import Invocation
from .models.jmap_request_envelope import JmapRequestEnvelope
from .models.jmap_response_envelope import JmapResponseEnvelope
from .models.mailbox import Mailbox, MailboxRights
from .models.email_address import EmailAddress
from .models.email_address_group import EmailAddressGroup
from .models.email_body_part import EmailBodyPart
from .models.email_header import EmailHeader
from .models.email import Email, EmailBodyValue
from .models.thread import Thread
from .models.identity import Identity
from .models.comparator import Comparator
from .models.search_snippet import SearchSnippet
from .models.envelope import Envelope, Address
from .models.delivery_status import DeliveryStatus
from .models.email_submission import EmailSubmission
from .client_mail import _MailClientMixin
from .client_submission import _SubmissionClientMixin

class JmapClient(_CoreClientMixin, _MailClientMixin, _SubmissionClientMixin):
    """Composes the core session/transport mixin with each requested module
    method mixin. See client_core.py for __enter__/__exit__.
    """


__all__ = ["JmapClient", "JmapClientOptions", "SetError", "MethodError", "ResultReference", "JmapError", "JmapProtocolError", "JmapNetworkError", "JmapTransport", "UrllibJmapTransport", "JmapHttpRequest", "JmapHttpResponse", "Session", "Account", "CoreCapability", "Invocation", "JmapRequestEnvelope", "JmapResponseEnvelope", "Mailbox", "MailboxRights", "EmailAddress", "EmailAddressGroup", "EmailBodyPart", "EmailHeader", "Email", "EmailBodyValue", "Thread", "Identity", "Comparator", "SearchSnippet", "Envelope", "Address", "DeliveryStatus", "EmailSubmission"]
