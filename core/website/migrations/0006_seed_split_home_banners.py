from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations


DEFAULT_BANNERS = [
    {
        "title": "لوازم یدکی کامیون و کامیونت",
        "subtitle": "تامین قطعات اصلی و با کیفیت برای انواع کامیون و کامیونت با بهترین قیمت",
        "button_text": "مشاهده محصولات",
        "image_alt": "لوازم یدکی کامیون و کامیونت",
        "image_file": "img1.jpg",
        "link": "/shop/product/grid/",
        "background_style": 1,
        "sort_order": 1,
    },
    {
        "title": "قطعات موتور و گیربکس",
        "subtitle": "انواع قطعات موتور، گیربکس و سیستم انتقال قدرت با گارانتی معتبر",
        "button_text": "مشاهده قطعات",
        "image_alt": "قطعات موتور و گیربکس",
        "image_file": "img2.jpg",
        "link": "/shop/product/grid/",
        "background_style": 2,
        "sort_order": 2,
    },
    {
        "title": "لوازم ترمز و سیستم تعلیق",
        "subtitle": "قطعات ترمز، دیسک، لنت، کمک فنر و تمامی لوازم سیستم تعلیق",
        "button_text": "مشاهده محصولات",
        "image_alt": "لوازم ترمز و سیستم تعلیق",
        "image_file": "img3.jpg",
        "link": "/shop/product/grid/",
        "background_style": 3,
        "sort_order": 3,
    },
]


def _banner_image_path(filename):
    path = Path(settings.BASE_DIR) / "static" / "img" / "900x900" / filename
    if path.is_file():
        return path
    base = Path(settings.BASE_DIR) / "static" / "img"
    for subdir in ("1920x800", "750x750", "600x600"):
        candidate = base / subdir / filename
        if candidate.is_file():
            return candidate
    return None


def seed_split_home_banners(apps, schema_editor):
    HomeBanner = apps.get_model("website", "HomeBanner")

    for item in DEFAULT_BANNERS:
        banner = HomeBanner.objects.filter(title=item["title"]).first()
        if banner is None:
            banner = HomeBanner(title=item["title"])

        banner.subtitle = item["subtitle"]
        banner.button_text = item["button_text"]
        banner.image_alt = item["image_alt"]
        banner.link = item["link"]
        banner.background_style = item["background_style"]
        banner.sort_order = item["sort_order"]
        banner.is_active = True
        banner.is_default = True

        if not banner.image:
            src = _banner_image_path(item["image_file"])
            if src is not None:
                with src.open("rb") as image_file:
                    banner.image.save(src.name, File(image_file), save=False)

        banner.save()


def unseed_split_home_banners(apps, schema_editor):
    HomeBanner = apps.get_model("website", "HomeBanner")
    titles = [item["title"] for item in DEFAULT_BANNERS]
    HomeBanner.objects.filter(title__in=titles, is_default=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0005_homebanner_content_fields"),
    ]

    operations = [
        migrations.RunPython(
            seed_split_home_banners,
            unseed_split_home_banners,
        ),
    ]
