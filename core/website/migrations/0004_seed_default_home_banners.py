from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations


def _static_banner_path(filename):
    base = Path(settings.BASE_DIR) / "static" / "img"
    for subdir in ("1920x800", "900x900", "750x750"):
        path = base / subdir / filename
        if path.is_file():
            return path
    return None


def seed_default_home_banners(apps, schema_editor):
    HomeBanner = apps.get_model("website", "HomeBanner")
    if HomeBanner.objects.exists():
        return

    defaults = [
        {
            "title": "لوازم یدکی کامیون و کامیونت",
            "image_file": "img1.jpg",
            "link": "/shop/product/grid/",
            "sort_order": 1,
        },
        {
            "title": "قطعات موتور و گیربکس",
            "image_file": "img2.jpg",
            "link": "/shop/product/grid/",
            "sort_order": 2,
        },
        {
            "title": "لوازم ترمز و سیستم تعلیق",
            "image_file": "img3.jpg",
            "link": "/shop/product/grid/",
            "sort_order": 3,
        },
    ]

    for item in defaults:
        src = _static_banner_path(item["image_file"])
        if src is None:
            continue
        banner = HomeBanner(
            title=item["title"],
            link=item["link"],
            sort_order=item["sort_order"],
            is_active=True,
        )
        with src.open("rb") as image_file:
            banner.image.save(src.name, File(image_file), save=True)


def unseed_default_home_banners(apps, schema_editor):
    HomeBanner = apps.get_model("website", "HomeBanner")
    titles = [
        "لوازم یدکی کامیون و کامیونت",
        "قطعات موتور و گیربکس",
        "لوازم ترمز و سیستم تعلیق",
    ]
    HomeBanner.objects.filter(title__in=titles).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0003_homebanner"),
    ]

    operations = [
        migrations.RunPython(
            seed_default_home_banners,
            unseed_default_home_banners,
        ),
    ]
