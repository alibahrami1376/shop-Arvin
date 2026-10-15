"""Jalali (Persian calendar) display filters for human-facing dates."""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import jdatetime
from django import template
from django.utils import timezone

register = template.Library()

TEHRAN = ZoneInfo("Asia/Tehran")


@register.filter
def jalali(value, fmt="%Y/%m/%d"):
    """Format a date/datetime as Jalali. Empty or invalid values become \"\"."""
    if value in (None, ""):
        return ""

    # datetime before date — datetime subclasses date
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            value = value.astimezone(TEHRAN)
        try:
            return jdatetime.datetime.fromgregorian(datetime=value).strftime(fmt)
        except (ValueError, OverflowError, OSError, TypeError):
            return ""

    if isinstance(value, date):
        try:
            return jdatetime.date.fromgregorian(date=value).strftime(fmt)
        except (ValueError, OverflowError, OSError, TypeError):
            return ""

    return ""
