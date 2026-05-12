from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from blog.models import Category as BlogCategory
from blog.models import Post
from dashboard.admin.forms import BlogCategoryForm, BlogPostForm
from dashboard.permissions import HasAdminAccessPermission


class AdminBlogPostListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/blog/post-list.html"
    model = Post
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = Post.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(title__icontains=search_q)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        else:
            queryset = queryset.order_by("-created_date")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context


class AdminBlogPostCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/blog/post-create.html"
    model = Post
    form_class = BlogPostForm
    success_message = "ایجاد پست با موفقیت انجام شد"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:blog-post-edit", kwargs={"pk": self.object.pk})


class AdminBlogPostEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/blog/post-edit.html"
    model = Post
    form_class = BlogPostForm
    success_message = "ویرایش پست با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:blog-post-edit", kwargs={"pk": self.get_object().pk})


class AdminBlogPostDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/blog/post-delete.html"
    model = Post
    success_url = reverse_lazy("dashboard:admin:blog-post-list")
    success_message = "حذف پست با موفقیت انجام شد"


class AdminBlogCategoryListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = "dashboard/admin/blog/blog-category-list.html"
    model = BlogCategory
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_queryset(self):
        queryset = BlogCategory.objects.all()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(name__icontains=search_q)
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        else:
            queryset = queryset.order_by("name")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.get_queryset().count()
        return context


class AdminBlogCategoryCreateView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/blog/blog-category-create.html"
    model = BlogCategory
    form_class = BlogCategoryForm
    success_url = reverse_lazy("dashboard:admin:blog-category-list")
    success_message = "ایجاد دسته‌بندی بلاگ با موفقیت انجام شد"


class AdminBlogCategoryEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = "dashboard/admin/blog/blog-category-edit.html"
    model = BlogCategory
    form_class = BlogCategoryForm
    success_message = "ویرایش دسته‌بندی بلاگ با موفقیت انجام شد"

    def get_success_url(self):
        return reverse_lazy("dashboard:admin:blog-category-edit", kwargs={"pk": self.get_object().pk})


class AdminBlogCategoryDeleteView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/blog/blog-category-delete.html"
    model = BlogCategory
    success_url = reverse_lazy("dashboard:admin:blog-category-list")
    success_message = "حذف دسته‌بندی بلاگ با موفقیت انجام شد"
