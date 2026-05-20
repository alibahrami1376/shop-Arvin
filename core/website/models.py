from django.db import models
from django.contrib.auth import get_user_model
from django.templatetags.static import static
from django_ckeditor_5.fields import CKEditor5Field

from website.logo_validation import SITE_LOGO_HEIGHT, SITE_LOGO_WIDTH


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
    class DisplayTarget(models.TextChoices):
        ALL = "all", "همه دستگاه‌ها"
        MOBILE = "mobile", "فقط موبایل"
        DESKTOP = "desktop", "فقط دسکتاپ"

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
    display_target = models.CharField(
        max_length=10,
        choices=DisplayTarget.choices,
        default=DisplayTarget.ALL,
        verbose_name="دستگاه نمایش",
    )
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


class SiteBrandingSettings(models.Model):
    """لوگوی اصلی سایت — یک ردیف؛ هدر، فوتر و فاکتور."""

    LOGO_WIDTH = SITE_LOGO_WIDTH
    LOGO_HEIGHT = SITE_LOGO_HEIGHT

    logo = models.ImageField(
        upload_to="branding/",
        blank=True,
        null=True,
        verbose_name="لوگوی سایت",
        help_text=f"PNG یا WEBP — دقیقاً {LOGO_WIDTH}×{LOGO_HEIGHT} پیکسل.",
    )
    site_name = models.CharField(
        max_length=120,
        blank=True,
        default="فروشگاه آروین",
        verbose_name="نام فروشگاه (متن alt لوگو)",
    )
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "لوگوی سایت"
        verbose_name_plural = "لوگوی سایت"

    def __str__(self):
        return "تنظیمات لوگو"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def has_custom_logo(self):
        return bool(self.logo)

    def get_logo_url(self):
        if self.logo:
            return self.logo.url
        return static("img/ghasetak.png")

    def get_logo_alt(self):
        return (self.site_name or "").strip() or "فروشگاه آروین"


class LegalPage(models.Model):
    class PageType(models.TextChoices):
        PRIVACY = "privacy", "حریم خصوصی"
        TERMS = "terms", "قوانین و مقررات"

    page_type = models.CharField(
        max_length=20,
        choices=PageType.choices,
        unique=True,
        verbose_name="نوع صفحه",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان")
    content = CKEditor5Field(verbose_name="محتوا")
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "صفحه قانونی"
        verbose_name_plural = "صفحات قانونی"

    def __str__(self):
        return self.get_page_type_display()

    @classmethod
    def get_by_type(cls, page_type):
        obj, _ = cls.objects.get_or_create(
            page_type=page_type,
            defaults={
                "title": cls.PageType(page_type).label,
                "content": f"<p>متن {cls.PageType(page_type).label} را از پنل مدیریت ویرایش کنید.</p>",
            },
        )
        return obj


class ContactPageSettings(models.Model):
    """تنظیمات نمایشی صفحه تماس با ما (یک ردیف)."""

    email = models.EmailField(
        blank=True,
        default="info@truckparts.ir",
        verbose_name="ایمیل",
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        default="۰۲۱-۱۲۳۴۵۶۷۸",
        verbose_name="تلفن",
    )
    working_hours = models.CharField(
        max_length=255,
        blank=True,
        default="شنبه تا پنجشنبه: ۹ صبح تا ۶ عصر",
        verbose_name="ساعات کاری",
    )
    instagram_link = models.CharField(max_length=500, blank=True, verbose_name="لینک اینستاگرام")
    telegram_link = models.CharField(max_length=500, blank=True, verbose_name="لینک تلگرام")
    linkedin_link = models.CharField(max_length=500, blank=True, verbose_name="لینک لینکدین")
    bale_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک بله",
        help_text="مثال: https://ble.ir/username",
    )
    rubika_link = models.CharField(max_length=500, blank=True, verbose_name="لینک روبیکا")
    bale_channel_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک کانال بله",
    )
    bale_channel_text = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="متن معرفی کانال بله",
        help_text="جمله‌ای که زیر لینک کانال نمایش داده می‌شود.",
    )
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات تماس با ما"
        verbose_name_plural = "تنظیمات تماس با ما"

    def __str__(self):
        return "تنظیمات تماس با ما"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_social_links(self):
        links = []
        for key, label, icon in (
            ("instagram", "اینستاگرام", "bi-instagram"),
            ("telegram", "تلگرام", "bi-telegram"),
            ("linkedin", "لینکدین", "bi-linkedin"),
            ("bale", "بله", None),
            ("rubika", "روبیکا", None),
        ):
            url = (getattr(self, f"{key}_link", "") or "").strip()
            if url:
                links.append({"key": key, "label": label, "url": url, "icon": icon})
        return links


class SiteWideSocialSettings(models.Model):
    """لینک شبکه‌های اجتماعی در فوتر و سایر بخش‌های عمومی سایت (جدا از بلوک صفحهٔ تماس با ما)."""

    instagram_link = models.CharField(max_length=500, blank=True, verbose_name="لینک اینستاگرام")
    telegram_link = models.CharField(max_length=500, blank=True, verbose_name="لینک تلگرام")
    linkedin_link = models.CharField(max_length=500, blank=True, verbose_name="لینک لینکدین")
    bale_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="لینک بله",
        help_text="مثال: https://ble.ir/username",
    )
    rubika_link = models.CharField(max_length=500, blank=True, verbose_name="لینک روبیکا")
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "شبکه‌های اجتماعی سایت"
        verbose_name_plural = "شبکه‌های اجتماعی سایت"

    def __str__(self):
        return "لینک‌های شبکه اجتماعی (فوتر و سایت)"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_links(self):
        links = []
        for key, label, icon in (
            ("instagram", "اینستاگرام", "bi-instagram"),
            ("telegram", "تلگرام", "bi-telegram"),
            ("linkedin", "لینکدین", "bi-linkedin"),
            ("bale", "بله", None),
            ("rubika", "روبیکا", None),
        ):
            url = (getattr(self, f"{key}_link", "") or "").strip()
            if url:
                links.append({"key": key, "label": label, "url": url, "icon": icon})
        return links