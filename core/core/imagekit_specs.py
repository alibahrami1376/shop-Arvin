"""Shared ImageKit specs — reuse across shop, blog, banners, …"""

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit


def product_card_image(source="image"):
    """List / home card — portrait 3:4 (540×720), keep ratio, no crop."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFit(540, 720)],
        format="WEBP",
        options={"quality": 82},
    )


def product_detail_image(source="image"):
    """PDP main gallery — fit inside 540×720, keep ratio, no crop."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFit(540, 720)],
        format="WEBP",
        options={"quality": 85},
    )


def blog_gallery_image(source="file"):
    """Blog extra images (keep aspect, max 800)."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFit(800, 800)],
        format="WEBP",
        options={"quality": 85},
    )


def product_thumb_image(source="image"):
    """Cart / order / wishlist thumbnail — portrait 3:4, no crop."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFit(90, 120)],
        format="WEBP",
        options={"quality": 78},
    )


def product_gallery_thumb_image(source="file"):
    """PDP gallery strip thumbs — portrait 3:4, no crop."""
    return ImageSpecField(
        source=source,
        processors=[ResizeToFit(90, 120)],
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
