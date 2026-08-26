from accounts.models import UserType
from django.contrib.auth.mixins import UserPassesTestMixin


class HasCustomerAccessPermission(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.type == UserType.customer.value
        return False
