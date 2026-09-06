import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from meta.models import ModelMeta
from shop.image_urls import safe_imagekit_url

from core.imagekit_specs import (
    blog_card_image,
    blog_gallery_image,
    blog_hero_image,
    product_gallery_thumb_image,
)

# fetching user model
User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام")

    class Meta:
        ordering = ["name"]
        verbose_name = "تگ"
        verbose_name_plural = "تگ‌ها"

    def __str__(self):
        return self.name


class Post(ModelMeta, models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="نویسنده"
    )
    image = models.ImageField(
        upload_to="blog/", default="blog/default.png", verbose_name="تصویر"
    )
    image_alt = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="متن alt تصویر",
        help_text="اگر خالی باشد، عنوان پست استفاده می‌شود.",
    )
    image_card = blog_card_image("image")
    image_hero = blog_hero_image("image")
    title = models.CharField(max_length=255, verbose_name="عنوان")
    slug = models.SlugField(
        max_length=255,
        allow_unicode=True,
        unique=True,
        verbose_name="اسلاگ",
    )
    content = CKEditor5Field(verbose_name="محتوا")
    url = models.URLField(max_length=500, null=True, blank=True, verbose_name="لینک")
    category = models.ManyToManyField(Category, verbose_name="دسته‌بندی")
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="posts", verbose_name="تگ‌ها"
    )
    counted_view = models.IntegerField(default=0, verbose_name="تعداد بازدید")
    status = models.BooleanField(default=False, verbose_name="وضعیت انتشار")
    published_date = models.DateTimeField(
        null=True, blank=True, verbose_name="تاریخ انتشار"
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    _metadata = {
        "title": "get_meta_title",
        "description": "get_meta_description",
        "image": "get_meta_image",
        "url": "get_absolute_url",
        "og_type": "article",
        "twitter_type": "summary_large_image",
        "schemaorg_type": "Article",
        "published_time": "published_date",
        "modified_time": "updated_date",
    }

    class Meta:
        ordering = ["-created_date"]
        verbose_name = "پست"
        verbose_name_plural = "پست‌ها"

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("blog:blog_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            from blog.utils import unique_post_slug

            self.slug = unique_post_slug(self.title, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def get_meta_description(self):
        from core.seo import normalize_meta_description

        return normalize_meta_description(self.content) or self.title

    def get_meta_title(self):
        return self.title

    def get_meta_image(self):
        return self.image_card_url or ""

    def as_json_ld(self) -> dict:
        """BlogPosting JSON-LD for rich results (one source from the model)."""
        from core.seo import absolute_site_url

        post_url = absolute_site_url(self.get_absolute_url())
        images = []
        for src in (self.image_hero_url, self.image_card_url):
            abs_src = absolute_site_url(src) if src else ""
            if abs_src and abs_src not in images:
                images.append(abs_src)

        published = self.published_date or self.created_date
        data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": self.title,
            "description": self.get_meta_description(),
            "url": post_url,
            "mainEntityOfPage": {"@type": "WebPage", "@id": post_url},
            "image": images or None,
            "datePublished": published.isoformat() if published else None,
            "dateModified": self.updated_date.isoformat(),
            "publisher": {
                "@type": "Organization",
                "name": settings.SITE_NAME,
            },
        }
        if self.author is not None:
            author_name = self.author.get_full_name()
            if author_name:
                data["author"] = {"@type": "Person", "name": author_name}
        return {key: value for key, value in data.items() if value is not None}

    def as_json_ld_json(self) -> str:
        return json.dumps(self.as_json_ld(), ensure_ascii=False, separators=(",", ":"))

    @property
    def image_card_url(self):
        return safe_imagekit_url(self, "image_card", "image")

    @property
    def image_hero_url(self):
        return safe_imagekit_url(self, "image_hero", "image")

    def get_image_alt(self):
        return (self.image_alt or "").strip() or self.title

    def get_content_html(self):
        from django.utils.safestring import mark_safe

        from core.seo import ensure_img_alts

        return mark_safe(ensure_img_alts(self.content, self.get_image_alt()))


class PostImageModel(models.Model):
    """تصاویر اضافی پست (گالری)، جدا از تصویر شاخص و تصاویر داخل متن ادیتور."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_images",
        verbose_name="پست",
    )
    file = models.ImageField(upload_to="blog/extra-img/", verbose_name="فایل تصویر")
    image_alt = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="متن alt تصویر",
        help_text="اگر خالی باشد، alt تصویر شاخص یا عنوان پست استفاده می‌شود.",
    )
    file_detail = blog_gallery_image("file")
    file_thumb = product_gallery_thumb_image("file")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        ordering = ["created_date"]
        verbose_name = "تصویر پست"
        verbose_name_plural = "تصاویر پست"

    def __str__(self):
        return f"{self.post_id}: {self.file.name}"

    @property
    def file_detail_url(self):
        return safe_imagekit_url(self, "file_detail", "file")

    @property
    def file_thumb_url(self):
        return safe_imagekit_url(self, "file_thumb", "file")

    def get_image_alt(self):
        custom = (self.image_alt or "").strip()
        if custom:
            return custom
        return self.post.get_image_alt()
