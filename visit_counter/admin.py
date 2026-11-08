from django.contrib import admin

from .models import UserVisit


class UserVisitAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "session_key", "remote_addr", "user_agent")
    list_filter = ("timestamp",)
    search_fields = (
        "user_acc__first_name",
        "user_acc__last_name",
        "user_acc__username",
        "ua_string",
    )
    raw_id_fields = ("user_acc",)
    readonly_fields = (
        "user_acc",
        "hash",
        "timestamp",
        "session_key",
        "remote_addr",
        "device",
        "os",
        "browser",
        "ua_string",
        "created_at",
    )
    ordering = ("-timestamp",)


admin.site.register(UserVisit, UserVisitAdmin)
