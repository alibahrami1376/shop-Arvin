import json
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from meta.models import ModelMeta

from core.imagekit_specs import (
    product_card_image,
    product_detail_image,
    product_gallery_thumb_image,
    product_thumb_image,
)
from shop.image_urls import safe_imagekit_url


class ProductStatusType(models.IntegerChoices):
    publish = 1, ("نمایش")
    draft = 2, ("عدم نمایش")


class ProductCategoryModel(models.Model):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته والد",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "دسته‌بندی محصول"
        verbose_name_plural = "دسته‌بندی‌های محصول"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("shop:product-category", kwargs={"slug": self.slug})

    def get_self_and_descendant_ids(self):
        if not self.pk:
            return []
        ids = [self.pk]
        for child in self.children.all():
            ids.extend(child.get_self_and_descendant_ids())
        return ids

    def get_indented_title(self, prefix="— "):
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        if depth == 0:
            return self.title
        return f"{prefix * depth}{self.title}"

    @classmethod
    def get_tree_ordered(cls):
        result = []

        def walk(parent=None):
            for category in cls.objects.filter(parent=parent).order_by("title"):
                result.append(category)
                walk(category)

        walk()
        return result


class ProductTagModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان")
    slug = models.SlugField(allow_unicode=True, unique=True, verbose_name="اسلاگ")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "تگ محصول"
        verbose_name_plural = "تگ‌های محصول"

    def __str__(self):
        return self.title


# Create your models here.
class ProductModel(ModelMeta, models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    category = models.ManyToManyField(ProductCategoryModel)
    tags = models.ManyToManyField(
        ProductTagModel, blank=True, related_name="products", verbose_name="تگ‌ها"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    image = models.ImageField(
        default="/default/product-image.png", upload_to="product/img/"
    )
    image_alt = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="متن alt تصویر",
        help_text="اگر خالی باشد، عنوان محصول استفاده می‌شود.",
    )
    image_card = product_card_image("image")
    image_detail = product_detail_image("image")
    image_thumb = product_thumb_image("image")
    description = models.TextField()
    brief_description = models.TextField(null=True, blank=True)

    stock = models.PositiveIntegerField(default=0)
    status = models.IntegerField(
        choices=ProductStatusType.choices, default=ProductStatusType.draft.value
    )
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    discount_percent = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    avg_rate = models.FloatField(default=0.0)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    _metadata = {
        "title": "get_meta_title",
        "description": "get_meta_description",
        "image": "get_meta_image",
        "url": "get_absolute_url",
        "og_type": "product",
        "twitter_type": "summary_large_image",
        "schemaorg_type": "Product",
    }

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title

    def get_price(self):
        discount_amount = self.price * Decimal(self.discount_percent / 100)
        discounted_amount = self.price - discount_amount
        return round(discounted_amount)

    def is_discounted(self):
        return self.discount_percent != 0

    def is_published(self):
        return self.status == ProductStatusType.publish.value

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("shop:product-detail", kwargs={"slug": self.slug})

    def get_meta_description(self):
        from core.seo import normalize_meta_description

        text = self.brief_description or self.description or self.title or ""
        return normalize_meta_description(text) or self.title

    def get_meta_title(self):
        return f"{self.title} - {settings.SITE_NAME}"

    def get_meta_image(self):
        return self.image_card_url or ""

    def as_json_ld(self) -> dict:
        """Product + Offer JSON-LD for rich results (one source from the model)."""
        from core.seo import absolute_site_url

        product_url = absolute_site_url(self.get_absolute_url())
        images = []
        for src in (
            self.image_detail_url,
            self.image_card_url,
            *(img.file_detail_url for img in self.product_images.all()),
        ):
            abs_src = absolute_site_url(src) if src else ""
            if abs_src and abs_src not in images:
                images.append(abs_src)

        availability = (
            "https://schema.org/InStock"
            if self.stock > 0
            else "https://schema.org/OutOfStock"
        )
        data = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": self.title,
            "description": self.get_meta_description(),
            "sku": str(self.pk),
            "url": product_url,
            "image": images,
            "brand": {"@type": "Brand", "name": settings.SITE_NAME},
            "offers": {
                "@type": "Offer",
                "url": product_url,
                "priceCurrency": "IRR",
                "price": str(int(self.get_price())),
                "availability": availability,
                "itemCondition": "https://schema.org/NewCondition",
            },
        }
        if self.avg_rate and self.avg_rate > 0:
            from review.models import ReviewModel, ReviewStatusType

            review_count = ReviewModel.objects.filter(
                product=self, status=ReviewStatusType.accepted.value
            ).count()
            if review_count:
                data["aggregateRating"] = {
                    "@type": "AggregateRating",
                    "ratingValue": round(float(self.avg_rate), 2),
                    "reviewCount": review_count,
                    "bestRating": 5,
                    "worstRating": 1,
                }
        return data

    def as_json_ld_json(self) -> str:
        return json.dumps(self.as_json_ld(), ensure_ascii=False, separators=(",", ":"))

    @property
    def image_card_url(self):
        return safe_imagekit_url(self, "image_card", "image")

    @property
    def image_detail_url(self):
        return safe_imagekit_url(self, "image_detail", "image")

    @property
    def image_thumb_url(self):
        return safe_imagekit_url(self, "image_thumb", "image")

    def get_image_alt(self):
        return (self.image_alt or "").strip() or self.title

    def get_description_html(self):
        from django.utils.safestring import mark_safe

        from core.seo import ensure_img_alts

        return mark_safe(ensure_img_alts(self.description, self.get_image_alt()))


class ProductImageModel(models.Model):
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name="product_images"
    )
    file = models.ImageField(upload_to="product/extra-img/")
    image_alt = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="متن alt تصویر",
        help_text="اگر خالی باشد، alt تصویر اصلی یا عنوان محصول استفاده می‌شود.",
    )
    file_detail = product_detail_image("file")
    file_thumb = product_gallery_thumb_image("file")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

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
        return self.product.get_image_alt()


class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.title
