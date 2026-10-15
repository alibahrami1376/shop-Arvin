from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase
from django.utils import timezone

from website.jalali_utils import (
    JALALI_DATETIME_FORMAT,
    format_jalali_datetime,
    normalize_digits,
    parse_jalali_datetime,
)

TEHRAN = ZoneInfo("Asia/Tehran")


class JalaliUtilsTests(SimpleTestCase):
    def test_normalize_digits(self):
        self.assertEqual(normalize_digits("۱۴۰۳/۰۱/۱۵ - ۱۴:۳۰"), "1403/01/15 - 14:30")

    def test_format_empty(self):
        self.assertEqual(format_jalali_datetime(None), "")
        self.assertEqual(format_jalali_datetime(""), "")

    def test_format_aware_datetime(self):
        value = datetime(2024, 3, 20, 14, 30, tzinfo=TEHRAN)
        self.assertEqual(
            format_jalali_datetime(value),
            "1403/01/01 - 14:30",
        )

    def test_parse_empty(self):
        self.assertIsNone(parse_jalali_datetime(None))
        self.assertIsNone(parse_jalali_datetime(""))
        self.assertIsNone(parse_jalali_datetime("   "))

    def test_parse_round_trip(self):
        value = datetime(2024, 6, 15, 14, 5, tzinfo=TEHRAN)
        text = format_jalali_datetime(value)
        parsed = parse_jalali_datetime(text)
        self.assertIsNotNone(parsed)
        self.assertTrue(timezone.is_aware(parsed))
        self.assertEqual(parsed.astimezone(TEHRAN), value)

    def test_parse_persian_digits(self):
        parsed = parse_jalali_datetime("۱۴۰۳/۰۱/۰۱ - ۱۴:۳۰")
        self.assertEqual(
            format_jalali_datetime(parsed, JALALI_DATETIME_FORMAT),
            "1403/01/01 - 14:30",
        )

    def test_parse_invalid(self):
        with self.assertRaises(ValueError):
            parse_jalali_datetime("not-a-date")
        with self.assertRaises(ValueError):
            parse_jalali_datetime("2024-03-20 14:30")
