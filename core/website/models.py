from django.db import models
from django.contrib.auth import get_user_model


# fetching user model
User = get_user_model()

# defining the status of items to be saved or released
class ContactModel(models.Model):

    full_name = models.CharField(max_length=200)
    email = models.EmailField(default=None, null=True)
    phone_number = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(max_length=700)
    is_seen = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.full_name


class NewsLetter(models.Model):
    email = models.EmailField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class FAQItem(models.Model):
    question = models.CharField(max_length=500, verbose_name="سوال")
    answer = models.TextField(verbose_name="پاسخ")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_published = models.BooleanField(default=True, verbose_name="منتشر شده")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-created_date"]
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"

    def __str__(self):
        return self.question


class HomeBanner(models.Model):
    STYLE_CHOICES = (
        (1, "سبک ۱"),
        (2, "سبک ۲"),
        (3, "سبک ۳"),
    )
    GRADIENT_STYLES = {
        1: "linear-gradient(135deg, rgba(232, 180, 160, 0.15), rgba(212, 165, 165, 0.15))",
        2: "linear-gradient(135deg, rgba(245, 230, 211, 0.2), rgba(232, 180, 160, 0.15))",
        3: "linear-gradient(135deg, rgba(212, 165, 165, 0.15), rgba(245, 230, 211, 0.2))",
    }

    title = models.CharField(max_length=200, verbose_name="عنوان")
    subtitle = models.TextField(blank=True, verbose_name="متن توضیح")
    button_text = models.CharField(
        max_length=100, blank=True, verbose_name="متن دکمه"
    )
    image = models.FileField(
        upload_to="banners/home/",
        verbose_name="تصویر یا GIF",
        help_text="فرمت‌های JPG، PNG، WEBP و GIF",
    )
    image_alt = models.CharField(
        max_length=200, blank=True, verbose_name="متن alt تصویر"
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک دکمه",
        help_text="مثال: /shop/product/grid/",
    )
    background_style = models.PositiveSmallIntegerField(
        choices=STYLE_CHOICES,
        default=1,
        verbose_name="سبک پس‌زمینه",
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_default = models.BooleanField(
        default=False,
        verbose_name="بنر پیش‌فرض",
        help_text="بنرهای پیش‌فرض فقط از پنل قابل فعال/غیرفعال شدن هستند.",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-created_date"]
        verbose_name = "بنر صفحه اصلی"
        verbose_name_plural = "بنرهای صفحه اصلی"

    def __str__(self):
        return self.title

    @property
    def is_gif(self):
        name = (self.image.name or "").lower()
        return name.endswith(".gif")

    @property
    def background_gradient(self):
        return self.GRADIENT_STYLES.get(self.background_style, self.GRADIENT_STYLES[1])