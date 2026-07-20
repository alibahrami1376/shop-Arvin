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



