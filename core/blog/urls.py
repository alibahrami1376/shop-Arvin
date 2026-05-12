from django.urls import path
from blog.views import BlogPostListView, blog_detail, blog_search

app_name = "blog"

urlpatterns = [
    path("", BlogPostListView.as_view(), name="blog_home"),
    path("<int:post_id>/", blog_detail, name="blog_detail"),
    path("category/<str:cat_name>/", BlogPostListView.as_view(), name="category"),
    path("search/", blog_search, name="search"),
]
