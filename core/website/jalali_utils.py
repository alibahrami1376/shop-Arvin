"""Shared Jalali format/parse helpers for display and admin form input."""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import jdatetime
from django.utils import timezone

TEHRAN = ZoneInfo("Asia/Tehran")

JALALI_DATE_FORMAT = "%Y/%m/%d"
JALALI_DATETIME_FORMAT = "%Y/%m/%d - %H:%M"

_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_digits(value: str) -> str:
    """Map Persian/Arabic-Indic digits to ASCII Latin digits."""
    return value.translate(_PERSIAN_DIGITS)


def format_jalali_datetime(value, fmt: str = JALALI_DATETIME_FORMAT) -> str:
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


def parse_jalali_datetime(value) -> datetime | None:
    """
    Parse a Jalali datetime string into an aware Gregorian datetime (Asia/Tehran).

    Accepts empty -> None. Raises ValueError on invalid non-empty input.
    """
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            return value.astimezone(TEHRAN)
        return timezone.make_aware(value, TEHRAN)

    text = normalize_digits(str(value).strip())
    if not text:
        return None

    try:
        jdt = jdatetime.datetime.strptime(text, JALALI_DATETIME_FORMAT)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid jalali datetime") from exc

    gregorian = jdt.togregorian()
    if timezone.is_aware(gregorian):
        return gregorian.astimezone(TEHRAN)
    return timezone.make_aware(gregorian, TEHRAN)
