import logging
import typing

import django.db
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import UserVisit

from .settings import DUPLICATE_LOG_LEVEL,  RECORDING_DISABLED, UNTRACKED

logger = logging.getLogger(__name__)


@django.db.transaction.atomic
def save_user_visit(user_visit: UserVisit) -> None:
    """Save the user visit and handle db.IntegrityError."""
    try:
        user_visit.save()
    except django.db.IntegrityError:
        getattr(logger, DUPLICATE_LOG_LEVEL)(
            "Error saving user visit (hash='%s')", user_visit.hash
        )


class UserVisitMiddleware:
    """Middleware to record user visits."""

    def __init__(self, get_response: typing.Callable) -> None:
        if RECORDING_DISABLED:
            raise MiddlewareNotUsed("UserVisit recording has been disabled")
        
        self.get_response = get_response


    def __call__(self, request: HttpRequest) -> typing.Optional[HttpResponse]:
        current_url = (request.path.split('/'))
        if current_url[1] not in UNTRACKED:
            # Save the user visit
            uv = UserVisit.objects.build(request, timezone.now())
            if not UserVisit.objects.filter(hash=uv.hash).exists():
                save_user_visit(uv)

        return self.get_response(request)
