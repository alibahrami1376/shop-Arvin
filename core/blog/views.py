
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.db.models import Q
from django.core.exceptions import FieldError
from blog.models import Post, Category


class BlogPostListView(ListView):
    model = Post
    template_name = "blog/blog-home.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_paginate_by(self, queryset):
        return self.request.GET.get("page_size", self.paginate_by)

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
        return context


def blog_detail(request, post_id):
    """
    نمایش جزئیات یک پست بلاگ
    """
    post = get_object_or_404(
        Post.objects.prefetch_related("post_images", "category", "author"),
        id=post_id,
        status=True,
    )

    # افزایش تعداد بازدید
    post.counted_view += 1
    post.save()

    # پست‌های مرتبط (از همان دسته‌بندی)
    related_posts = Post.objects.filter(
        category__in=post.category.all(),
        status=True
    ).exclude(id=post.id).distinct()[:3]

    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/blog-detail.html', context)


def blog_search(request):
    """
    جستجو در پست‌های بلاگ
    """
    query = request.GET.get('q', '')
    posts = Post.objects.filter(status=True)

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'query': query,
    }
    return render(request, 'blog/blog-search.html', context)
