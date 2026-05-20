from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from dashboard.admin.forms import LegalPageForm
from dashboard.permissions import HasAdminAccessPermission
from website.models import LegalPage


class AdminLegalPageUpdateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = LegalPage
    form_class = LegalPageForm
    template_name = "dashboard/admin/legal/legal-page-edit.html"

    def dispatch(self, request, *args, **kwargs):
        page_type = self.kwargs.get("page_type")
        if page_type not in LegalPage.PageType.values:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return LegalPage.get_by_type(self.kwargs["page_type"])

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:legal-page-edit",
            kwargs={"page_type": self.kwargs["page_type"]},
        )

    def get_success_message(self, cleaned_data):
        return f"متن «{self.object.get_page_type_display()}» با موفقیت ذخیره شد."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_type_label"] = self.object.get_page_type_display()
        return context
