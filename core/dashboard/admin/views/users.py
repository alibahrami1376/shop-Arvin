from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import (
    HasAdminAccessPermission,
    HasSuperUserAccessPermission,
    user_can_create_users,
    user_can_manage_roles,
)
from django.db.models import F, Q
from django.core import exceptions
from django.contrib.auth import get_user_model
from accounts.models import UserType
from dashboard.admin.forms import *

User = get_user_model()


def _manageable_users():
    return User.objects.filter(is_superuser=False).exclude(type=UserType.superuser.value)


class UserListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    title = "لیست کاربران"
    template_name = "dashboard/admin/users/user-list.html"
    paginate_by = 10
    ordering = "-created_date"

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        queryset = User.objects.filter(is_superuser=False).exclude(
            type=UserType.superuser.value
        ).order_by("-created_date")
        search_query = self.request.GET.get('q', None)
        ordering_query = self.request.GET.get('ordering', None)

        if search_query:
            queryset = queryset.filter(
                Q(email__icontains=search_query) | Q(phone_number__icontains=search_query)
            )
        if ordering_query:
            try:
                queryset = queryset.order_by(ordering_query)
            except exceptions.FieldError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_result"] = self.get_queryset().count()
        context["can_create_user"] = user_can_create_users(self.request.user)
        return context


class UserCreateView(LoginRequiredMixin, HasSuperUserAccessPermission, SuccessMessageMixin, CreateView):
    title = "ساخت کاربر"
    template_name = "dashboard/admin/users/user-create.html"
    form_class = UserCreateForm
    success_message = "کاربر با موفقیت ساخته شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:user-edit", kwargs={"pk": self.object.pk})


class UserDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    title = "حذف کاربر"
    template_name = "dashboard/admin/users/user-delete.html"
    success_url = reverse_lazy("dashboard:admin:user-list")
    success_message = "کاربر مورد نظر با موفقیت حذف شد"

    def get_queryset(self):
        return _manageable_users()


class UserUpdateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    title = "ویرایش کاربر"
    template_name = "dashboard/admin/users/user-edit.html"
    success_message = "کاربر مورد نظر با موفقیت ویرایش شد"
    form_class = UserForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["can_change_type"] = user_can_manage_roles(self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_change_type"] = user_can_manage_roles(self.request.user)
        return context

    def get_success_url(self) -> str:
        return reverse_lazy("dashboard:admin:user-edit", kwargs={"pk": self.kwargs.get("pk")})

    def get_queryset(self):
        return _manageable_users()
