"""Shared ImageKit specs — reuse across shop, blog, banners, …"""

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit


def product_card_image(source="image"):
    """List / home card (~400×400)."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFill(400, 400)],
        format="WEBP",
        options={"quality": 82},
    )


def product_detail_image(source="image"):
    """PDP main gallery (~800×800, keep aspect)."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFit(800, 800)],
        format="WEBP",
        options={"quality": 85},
    )


def product_thumb_image(source="image"):
    """Cart / order / wishlist thumbnail."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFill(120, 120)],
        format="WEBP",
        options={"quality": 78},
    )


def product_gallery_thumb_image(source="file"):
    """PDP gallery strip thumbs."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFill(120, 120)],
        format="WEBP",
        options={"quality": 78},
    )


def blog_card_image(source="image"):
    """Blog list / home / related card cover."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFill(640, 360)],
        format="WEBP",
        options={"quality": 82},
    )


def blog_hero_image(source="image"):
    """Blog detail hero (keep aspect, max width)."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFit(1200, 675)],
        format="WEBP",
        options={"quality": 85},
    )


def banner_display_image(source="image"):
    """
    Home banners: keep aspect (no crop), cap huge uploads, compress to WebP.
    Display size stays CSS-controlled — only file weight drops.
    """
    return ImageSpecField(
        source=source,
        processors=[ResizeToFit(1920, 1080)],
        format="WEBP",
        options={"quality": 72},
    )
