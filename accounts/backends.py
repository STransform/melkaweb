from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class FlexibleModelBackend(ModelBackend):
    """
    Authenticate with either email or username, depending on which fields
    exist on the active user model.
    """

    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        UserModel = get_user_model()
        identifier = (email or username or kwargs.get(UserModel.USERNAME_FIELD) or "").strip()
        if not identifier or password is None:
            return None

        lookup = Q()
        username_field = UserModel.USERNAME_FIELD
        concrete_fields = {field.name for field in UserModel._meta.concrete_fields}

        if username_field in concrete_fields:
            lookup |= Q(**{f"{username_field}__iexact": identifier})

        if "email" in concrete_fields:
            lookup |= Q(email__iexact=identifier)

        if not lookup:
            return None

        try:
            user = UserModel._default_manager.get(lookup)
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            user = UserModel._default_manager.filter(lookup).order_by("pk").first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
