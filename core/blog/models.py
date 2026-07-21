from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

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


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="نویسنده")
    image = models.ImageField(upload_to="blog/", default="blog/default.png", verbose_name="تصویر")
    title = models.CharField(max_length=255, verbose_name="عنوان")
    content = CKEditor5Field(verbose_name="محتوا")
    url = models.URLField(max_length=500, null=True, blank=True, verbose_name="لینک")
    category = models.ManyToManyField(Category, verbose_name="دسته‌بندی")
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name="تگ‌ها")
    counted_view = models.IntegerField(default=0, verbose_name="تعداد بازدید")
    status = models.BooleanField(default=False, verbose_name="وضعیت انتشار")
    published_date = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ انتشار")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        ordering = ["-created_date"]
        verbose_name = "پست"
        verbose_name_plural = "پست‌ها"

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("blog:blog_detail", args=[str(self.id)])


class PostImageModel(models.Model):
    """تصاویر اضافی پست (گالری)، جدا از تصویر شاخص و تصاویر داخل متن ادیتور."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_images",
        verbose_name="پست",
    )
    file = models.ImageField(upload_to="blog/extra-img/", verbose_name="فایل تصویر")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        ordering = ["created_date"]
        verbose_name = "تصویر پست"
        verbose_name_plural = "تصاویر پست"

    def __str__(self):
        return f"{self.post_id}: {self.file.name}"
