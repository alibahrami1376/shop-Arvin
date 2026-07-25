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
