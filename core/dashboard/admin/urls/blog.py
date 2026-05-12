from django.urls import path

from .. import views

urlpatterns = [
    path("blog/post/list/", views.AdminBlogPostListView.as_view(), name="blog-post-list"),
    path("blog/post/create/", views.AdminBlogPostCreateView.as_view(), name="blog-post-create"),
    path("blog/post/<int:pk>/edit/", views.AdminBlogPostEditView.as_view(), name="blog-post-edit"),
    path("blog/post/<int:pk>/delete/", views.AdminBlogPostDeleteView.as_view(), name="blog-post-delete"),
    path(
        "blog/category/list/",
        views.AdminBlogCategoryListView.as_view(),
        name="blog-category-list",
    ),
    path(
        "blog/category/create/",
        views.AdminBlogCategoryCreateView.as_view(),
        name="blog-category-create",
    ),
    path(
        "blog/category/<int:pk>/edit/",
        views.AdminBlogCategoryEditView.as_view(),
        name="blog-category-edit",
    ),
    path(
        "blog/category/<int:pk>/delete/",
        views.AdminBlogCategoryDeleteView.as_view(),
        name="blog-category-delete",
    ),
]
