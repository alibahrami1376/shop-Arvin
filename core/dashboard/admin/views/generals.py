from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.views.generic import TemplateView

from dashboard.permissions import HasAdminAccessPermission
from accounts.models import User, UserType
from order.models import OrderModel, OrderStatusType
from payment.models import PaymentModel, PaymentStatusType
from shop.models import ProductModel
from website.models import ContactModel
from review.models import ReviewModel, ReviewStatusType


class AdminDashboardHomeView(LoginRequiredMixin, HasAdminAccessPermission, TemplateView):
    template_name = "dashboard/admin/home.html"

    def _get_user_role_label(self, user):
        if user.is_superuser:
            return "سوپریوزر"
        role_map = {
            UserType.admin.value: "ادمین",
            UserType.superuser.value: "سوپریوزر",
            UserType.marketer.value: "مارکتر",
            UserType.editor.value: "ویراستار",
            UserType.support.value: "پشتیبانی",
            UserType.customer.value: "مشتری",
        }
        return role_map.get(user.type, "کاربر")

    def _has_any_perm(self, user, perms):
        if user.is_superuser:
            return True
        return any(user.has_perm(perm) for perm in perms)

    def _get_permission_badges(self, user):
        return [
            {
                "label": "سفارشات",
                "granted": self._has_any_perm(
                    user,
                    [
                        "order.view_ordermodel",
                        "order.change_ordermodel",
                    ],
                ),
            },
            {
                "label": "محصولات",
                "granted": self._has_any_perm(
                    user,
                    [
                        "shop.view_productmodel",
                        "shop.change_productmodel",
                    ],
                ),
            },
            {
                "label": "مشتریان",
                "granted": self._has_any_perm(
                    user,
                    [
                        "accounts.view_user",
                        "accounts.change_user",
                    ],
                ),
            },
            {
                "label": "بلاگ",
                "granted": self._has_any_perm(
                    user,
                    [
                        "blog.view_post",
                        "blog.change_post",
                    ],
                ),
            },
            {
                "label": "تنظیمات",
                "granted": self._has_any_perm(
                    user,
                    [
                        "website.change_sitebrandingsettings",
                        "website.change_contactpagesettings",
                        "payment.change_paymentmethodsettings",
                    ],
                ),
            },
            {
                "label": "کاربران",
                "granted": self._has_any_perm(
                    user,
                    [
                        "accounts.view_user",
                        "accounts.add_user",
                        "accounts.change_user",
                    ],
                ),
            },
        ]

    def _get_user_initials(self, user):
        profile = user.user_profile
        letters = []
        if profile.first_name:
            letters.append(profile.first_name.strip()[:1])
        if profile.last_name:
            letters.append(profile.last_name.strip()[:1])
        if not letters and user.email:
            letters.append(user.email.strip()[:1])
        if not letters and user.phone_number:
            letters.append(user.phone_number.strip()[-2:])
        return "".join(letters[:2]).upper() or "AU"

    def _has_custom_avatar(self, user):
        image = getattr(user.user_profile, "image", None)
        if not image:
            return False
        image_name = (getattr(image, "name", "") or "").lower()
        return bool(image_name and not image_name.endswith("profile/default.png"))

    def _get_active_session_count(self, user):
        active_count = 0
        for session in Session.objects.filter(expire_date__gte=timezone.now()):
            data = session.get_decoded()
            if str(data.get("_auth_user_id")) == str(user.pk):
                active_count += 1
        return active_count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = user.user_profile
        now = timezone.localtime()

        context["orders_count"] = OrderModel.objects.count()
        context["orders_success_count"] = OrderModel.objects.filter(status=OrderStatusType.success.value).count()
        context["orders_pending_count"] = OrderModel.objects.filter(status=OrderStatusType.pending.value).count()
        context["users_count"] = User.objects.filter(type=UserType.customer.value).count()
        context["products_count"] = ProductModel.objects.count()
        context["contacts_count"] = ContactModel.objects.count()
        context["reviews_count"] = ReviewModel.objects.count()
        context["recent_orders"] = OrderModel.objects.select_related("user").order_by("-created_date")[:8]
        context["dashboard_now"] = now
        context["dashboard_user"] = user
        context["dashboard_profile"] = profile
        context["dashboard_user_full_name"] = profile.get_fullname()
        context["dashboard_user_role"] = self._get_user_role_label(user)
        context["dashboard_groups"] = list(user.groups.values_list("name", flat=True))
        context["dashboard_permission_badges"] = self._get_permission_badges(user)
        context["dashboard_has_custom_avatar"] = self._has_custom_avatar(user)
        context["dashboard_user_initials"] = self._get_user_initials(user)
        context["dashboard_last_profile_update"] = profile.updated_date
        context["dashboard_password_last_changed"] = user.updated_date
        context["dashboard_active_session_count"] = self._get_active_session_count(user)
        context["notification_pending_payments"] = PaymentModel.objects.filter(
            status=PaymentStatusType.awaiting_payment.value
        ).count()
        context["notification_pending_comments"] = ReviewModel.objects.filter(
            status=ReviewStatusType.pending.value
        ).count()
        context["notification_low_stock_products"] = ProductModel.objects.filter(stock__lte=3).count()
        context["notification_new_support_tickets"] = ContactModel.objects.filter(
            is_seen=False
        ).count()
        return context
