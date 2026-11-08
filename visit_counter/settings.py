from os import getenv
from typing import Any, Callable

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest


def _env_or_setting(key: str, default: Any, cast_func: Callable = lambda x: x) -> Any:
    return cast_func(getenv(key) or getattr(settings, key, default))


RECORDING_DISABLED = _env_or_setting(
    "USER_VISIT_RECORDING_DISABLED", False, lambda x: bool(x)
)




# The log level to use when logging duplicate hashes. This is WARNING by
# default, but if it's noisy you can turn this down by setting this
# value. Must be one of "debug", "info", "warning", "error"
DUPLICATE_LOG_LEVEL: str = getattr(
    settings, "USER_VISIT_DUPLICATE_LOG_LEVEL", "warning"
).lower()

UNTRACKED = ['media','static','admin','dashboard','documents','jsi18n', 'i18n', 'filer', 'translator']

