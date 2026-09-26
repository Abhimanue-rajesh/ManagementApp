import os
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
MAILBOX = "ticket@thedeepseafood.com"
STATE_SESSION_KEY = "ticket_mailbox_oauth_state"


def _admin_only(request):
    # Only a full system admin should connect or replace the mailbox account.
    if not request.user.is_superuser:
        raise PermissionDenied


def _flow(state=None):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH_CLIENT_FILE,
        scopes=SCOPES,
        state=state,
    )
    flow.redirect_uri = settings.GOOGLE_TICKET_REDIRECT_URI
    return flow


def _save_credentials(credentials):
    token_path = Path(settings.GOOGLE_TICKET_TOKEN_FILE)
    token_path.parent.mkdir(parents=True, exist_ok=True)

    # Write a private temporary file, then replace the token file.
    fd, temporary_path = tempfile.mkstemp(
        prefix=".google-ticket-",
        dir=token_path.parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(credentials.to_json())
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, token_path)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)


@staff_member_required
@require_GET
def connect(request):
    _admin_only(request)

    flow = _flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )
    request.session[STATE_SESSION_KEY] = state
    return redirect(authorization_url)


@staff_member_required
@require_GET
def callback(request):
    _admin_only(request)

    expected_state = request.session.pop(STATE_SESSION_KEY, None)
    if not expected_state or request.GET.get("state") != expected_state:
        return HttpResponseBadRequest("Invalid OAuth state.")

    if request.GET.get("error"):
        return HttpResponseBadRequest("Google authorization was not granted.")

    flow = _flow(state=expected_state)
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials
    if not credentials.refresh_token:
        return HttpResponseBadRequest(
            "No refresh token was returned. Reconnect the mailbox."
        )

    service = build("gmail", "v1", credentials=credentials)
    profile = service.users().getProfile(userId="me").execute()

    if profile["emailAddress"].lower() != MAILBOX:
        return HttpResponseBadRequest(
            "Wrong Google account. Sign in as ticket@thedeepseafood.com."
        )

    _save_credentials(credentials)
    return HttpResponse(
        "ticket@thedeepseafood.com connected successfully. "
        "You can now run the email fetch test."
    )
