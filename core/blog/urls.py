from django.urls import path
from blog.views import blog_home, blog_detail, blog_search

app_name = "blog"

urlpatterns = [
    path("", blog_home, name="blog_home"),
    path("<int:post_id>/", blog_detail, name="blog_detail"),
    path("category/<str:cat_name>/", blog_home, name="category"),
    path("search/", blog_search, name="search"),
]
