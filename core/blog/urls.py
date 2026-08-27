from django.urls import path, re_path

from blog.views import (
    BlogPostListView,
    blog_detail,
    blog_detail_id_redirect,
    blog_search,
)

app_name = "blog"

urlpatterns = [
    path("", BlogPostListView.as_view(), name="blog_home"),
    path("search/", blog_search, name="search"),
    path("category/<str:cat_name>/", BlogPostListView.as_view(), name="category"),
    # Legacy indexed URLs: /blog/<id>/ → /blog/<slug>/
    path("<int:post_id>/", blog_detail_id_redirect, name="blog_detail_legacy"),
    re_path(r"(?P<slug>[-\w]+)/$", blog_detail, name="blog_detail"),
]
