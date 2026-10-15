import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from payment.bale_client import BaleAPIError, BaleClient
from payment.bale_config import build_bale_webhook_url, get_bale_config
from payment.models import BaleBotSettings

from dashboard.admin.forms.bale_bot_settings import BaleBotSettingsForm
from dashboard.permissions import HasAdminAccessPermission


class AdminBaleBotSettingsView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = BaleBotSettings
    form_class = BaleBotSettingsForm
    template_name = "dashboard/admin/payment/bale-bot-settings.html"
    success_url = reverse_lazy("dashboard:admin:bale-bot-settings")
    success_message = "تنظیمات بله با موفقیت ذخیره شد."

    def get_object(self, queryset=None):
        return BaleBotSettings.get_solo()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cfg = get_bale_config()
        context["webhook_url"] = build_bale_webhook_url()
        context["bale_configured"] = cfg.is_configured
        context["has_bot_token"] = bool(cfg.bot_token)
        context["has_webhook_secret"] = bool(cfg.webhook_secret)
        context["webhook_info_json"] = self.request.session.pop(
            "bale_webhook_info", None
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = (request.POST.get("action") or "save").strip()
        if action in {"set_webhook", "get_webhook_info", "delete_webhook"}:
            return self._handle_webhook_action(action)
        return super().post(request, *args, **kwargs)

    def _handle_webhook_action(self, action: str):
        cfg = get_bale_config()
        if not cfg.bot_token:
            messages.error(
                self.request,
                "ابتدا توکن ربات را ذخیره کنید، سپس وب‌هوک را ست کنید.",
            )
            return redirect(self.success_url)

        client = BaleClient()
        try:
            if action == "set_webhook":
                if not cfg.webhook_secret:
                    messages.error(
                        self.request,
                        "رمز وب‌هوک خالی است. ابتدا رمز را ذخیره کنید.",
                    )
                    return redirect(self.success_url)
                url = build_bale_webhook_url()
                result = client.set_webhook(url)
                messages.success(
                    self.request,
                    f"وب‌هوک ست شد: {url}",
                )
                self.request.session["bale_webhook_info"] = json.dumps(
                    result, ensure_ascii=False, indent=2, default=str
                )
            elif action == "get_webhook_info":
                result = client.get_webhook_info()
                messages.info(self.request, "وضعیت وب‌هوک از بله دریافت شد.")
                self.request.session["bale_webhook_info"] = json.dumps(
                    result, ensure_ascii=False, indent=2, default=str
                )
            elif action == "delete_webhook":
                result = client.delete_webhook()
                messages.warning(self.request, "وب‌هوک حذف شد.")
                self.request.session["bale_webhook_info"] = json.dumps(
                    result, ensure_ascii=False, indent=2, default=str
                )
        except BaleAPIError as exc:
            messages.error(self.request, f"خطای API بله: {exc}")

        return redirect(self.success_url)
