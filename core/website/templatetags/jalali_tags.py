"""Jalali (Persian calendar) display filters for human-facing dates."""

from __future__ import annotations

from django import template

from website.jalali_utils import JALALI_DATE_FORMAT, format_jalali_datetime

register = template.Library()


@register.filter
def jalali(value, fmt=JALALI_DATE_FORMAT):
    """Format a date/datetime as Jalali. Empty or invalid values become \"\"."""
    return format_jalali_datetime(value, fmt)
