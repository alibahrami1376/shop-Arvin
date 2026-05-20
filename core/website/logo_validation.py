from django.core.exceptions import ValidationError

SITE_LOGO_WIDTH = 200
SITE_LOGO_HEIGHT = 222
SITE_LOGO_MAX_BYTES = 400 * 1024
SITE_LOGO_ALLOWED_FORMATS = {"PNG", "WEBP"}


def validate_site_logo_image(uploaded_file):
    """لوگو باید دقیقاً 200×222 پیکسل و فرمت PNG یا WEBP باشد."""
    if not uploaded_file:
        return

    size = getattr(uploaded_file, "size", None)
    if size and size > SITE_LOGO_MAX_BYTES:
        raise ValidationError(
            f"حجم فایل نباید بیشتر از {SITE_LOGO_MAX_BYTES // 1024} کیلوبایت باشد."
        )

    try:
        from PIL import Image
    except ImportError as exc:
        raise ValidationError("کتابخانهٔ پردازش تصویر نصب نیست.") from exc

    try:
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as img:
            img_format = (img.format or "").upper()
            if img_format == "JPG":
                img_format = "JPEG"
            width, height = img.size
    except Exception as exc:
        raise ValidationError("فایل تصویر معتبر نیست یا قابل خواندن نیست.") from exc
    finally:
        uploaded_file.seek(0)

    if img_format not in SITE_LOGO_ALLOWED_FORMATS:
        allowed = " یا ".join(sorted(SITE_LOGO_ALLOWED_FORMATS))
        raise ValidationError(
            f"فرمت مجاز: {allowed}. لوگو را با پس‌زمینهٔ شفاف آپلود کنید. "
            f"(فایل شما: {img_format or 'نامشخص'})"
        )

    if width != SITE_LOGO_WIDTH or height != SITE_LOGO_HEIGHT:
        raise ValidationError(
            f"ابعاد لوگو باید دقیقاً {SITE_LOGO_WIDTH}×{SITE_LOGO_HEIGHT} پیکسل باشد "
            f"(نسبت تصویر ثابت). ابعاد فایل شما: {width}×{height} پیکسل."
        )
