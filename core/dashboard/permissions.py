from django.contrib.auth.mixins import UserPassesTestMixin
from accounts.models import UserType


class HasCustomerAccessPermission(UserPassesTestMixin):

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.type == UserType.customer.value
        return False
    


class HasAdminAccessPermission(UserPassesTestMixin):

    allowed_types = (
        UserType.admin.value,
        UserType.superuser.value,
    )

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            self.request.user.type in self.allowed_types
        )


class HasSuperUserAccessPermission(UserPassesTestMixin):
    """Only Django superuser or users with type=superuser."""

    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated
            and (user.is_superuser or user.type == UserType.superuser.value)
        )


def user_can_manage_roles(user):
    """Superuser and admin can change another user's type/status."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.type in (
        UserType.admin.value,
        UserType.superuser.value,
    )


def user_can_create_users(user):
    """Only superuser can create users."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.type == UserType.superuser.value

