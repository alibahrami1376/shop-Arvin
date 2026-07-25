from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Category as BlogCategory
from blog.models import Post
from shop.models import ProductCategoryModel, ProductModel, ProductStatusType


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "website:index",
            "website:about",
            "website:contact",
            "website:faq",
            "website:privacy",
            "website:terms",
            "shop:product-grid",
            "blog:blog_home",
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return ProductModel.objects.filter(
            status=ProductStatusType.publish.value
        ).order_by("-updated_date")

    def lastmod(self, obj):
        return obj.updated_date


class ProductCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return ProductCategoryModel.objects.order_by("id")

    def lastmod(self, obj):
        return obj.updated_date

    def location(self, obj):
        return f"{reverse('shop:product-grid')}?category_id={obj.pk}"


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status=True).order_by("-updated_date")

    def lastmod(self, obj):
        return obj.updated_date


class BlogCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return BlogCategory.objects.order_by("name")

    def location(self, obj):
        return reverse("blog:category", kwargs={"cat_name": obj.name})
