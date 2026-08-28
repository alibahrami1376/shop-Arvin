from django.conf import settings
from django.core.exceptions import FieldError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from meta.views import Meta

from blog.models import Category, Post
from core.seo import (
    breadcrumb_for_blog_list,
    breadcrumb_for_blog_post,
    breadcrumb_json_ld,
    normalize_meta_description,
)
from core.views_meta import SiteMetadataMixin


class BlogPostListView(SiteMetadataMixin, ListView):
    model = Post
    template_name = "blog/blog-home.html"
    context_object_name = "posts"
    paginate_by = 9
    description = (
        "مقالات و راهنماهای فروشگاه آروین درباره صندلی کامیون، "
        "سبک زندگی در جاده و خرید هوشمند؛ "
        "تازه‌ترین مطالب تخصصی را در بلاگ آروین بخوانید."
    )

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

    def get_meta_title(self, context=None):
        if q := self.request.GET.get("q"):
            return f"جستجو: {q} - بلاگ {settings.SITE_NAME}"
        cat_name = self.kwargs.get("cat_name")
        if cat_name:
            return f"{cat_name} - بلاگ {settings.SITE_NAME}"
        return super().get_meta_title(context)

    def get_meta_description(self, context=None):
        cat_name = self.kwargs.get("cat_name")
        if cat_name:
            return normalize_meta_description(
                f"مقالات دسته «{cat_name}» در بلاگ فروشگاه آروین؛ "
                f"راهنما و نکات کاربردی درباره لوازم کامیون و خرید هوشمند."
            )
        return super().get_meta_description(context)

    def get_queryset(self):
        queryset = Post.objects.filter(status=True).prefetch_related(
            "category", "author"
        )
        if cat_name := self.kwargs.get("cat_name"):
            queryset = queryset.filter(category__name=cat_name).distinct()
        if search_q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(title__icontains=search_q) | Q(content__icontains=search_q)
            )
        if category_id := self.request.GET.get("category_id"):
            queryset = queryset.filter(category__id=category_id).distinct()
        if order_by := self.request.GET.get("order_by"):
            try:
                queryset = queryset.order_by(order_by)
            except FieldError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = context["page_obj"]
        context["total_items"] = self.get_queryset().count()
        context["categories"] = Category.objects.all()
        context["category"] = self.kwargs.get("cat_name")
        context["query"] = self.request.GET.get("q", "")
        items = breadcrumb_for_blog_list(cat_name=self.kwargs.get("cat_name"))
        context["breadcrumb_items"] = items
        context["breadcrumb_json_ld"] = breadcrumb_json_ld(items)
        return context


def blog_detail_id_redirect(request, post_id):
    """301 from legacy /blog/<id>/ URLs to the slug canonical."""
    post = get_object_or_404(Post, pk=post_id)
    return redirect(post.get_absolute_url(), permanent=True)


def blog_detail(request, slug):
    """نمایش جزئیات یک پست بلاگ."""
    post = get_object_or_404(
        Post.objects.prefetch_related("post_images", "category", "author"),
        slug=slug,
        status=True,
    )

    # افزایش تعداد بازدید
    post.counted_view += 1
    post.save(update_fields=["counted_view", "updated_date"])

    # پست‌های مرتبط (از همان دسته‌بندی)
    related_posts = (
        Post.objects.filter(category__in=post.category.all(), status=True)
        .exclude(id=post.id)
        .distinct()[:3]
    )

    items = breadcrumb_for_blog_post(post)
    context = {
        "post": post,
        "related_posts": related_posts,
        "meta": post.as_meta(request),
        "breadcrumb_items": items,
        "breadcrumb_json_ld": breadcrumb_json_ld(items),
    }
    return render(request, "blog/blog-detail.html", context)


def blog_search(request):
    """
    جستجو در پست‌های بلاگ
    """
    query = request.GET.get("q", "")
    posts = Post.objects.filter(status=True)

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))

    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    title = f"جستجو در بلاگ - {settings.SITE_NAME}"
    if query:
        title = f"جستجو: {query} - بلاگ {settings.SITE_NAME}"

    context = {
        "posts": page_obj,
        "query": query,
        "meta": Meta(
            title=title,
            description=normalize_meta_description(
                f"نتایج جستجو برای «{query}» در بلاگ فروشگاه آروین؛ "
                f"مقالات مرتبط با لوازم کامیون و راهنمای خرید را پیدا کنید."
                if query
                else (
                    "جستجو در مقالات بلاگ فروشگاه آروین؛ "
                    "راهنما و مطالب تخصصی درباره لوازم کامیون را سریع پیدا کنید."
                )
            ),
            url=request.path,
            use_og=True,
            use_twitter=True,
            use_sites=True,
            site_name=settings.SITE_NAME,
        ),
    }
    return render(request, "blog/blog-search.html", context)
