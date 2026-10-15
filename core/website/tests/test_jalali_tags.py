from datetime import date, datetime
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase
from django.utils import timezone

from website.templatetags.jalali_tags import jalali

TEHRAN = ZoneInfo("Asia/Tehran")


class JalaliFilterTests(SimpleTestCase):
    def test_none_and_empty(self):
        self.assertEqual(jalali(None), "")
        self.assertEqual(jalali(""), "")

    def test_invalid_type(self):
        self.assertEqual(jalali(123), "")
        self.assertEqual(jalali("foo"), "")
        self.assertEqual(jalali([]), "")

    def test_naive_datetime(self):
        value = datetime(2024, 3, 20, 12, 30, 0)
        self.assertEqual(jalali(value), "1403/01/01")
        self.assertEqual(
            jalali(value, "%Y/%m/%d - %H:%M"),
            "1403/01/01 - 12:30",
        )

    def test_datetime_time_format_aware(self):
        value = datetime(2024, 6, 15, 14, 5, tzinfo=TEHRAN)
        self.assertEqual(
            jalali(value, "%Y/%m/%d - %H:%M"),
            "1403/03/26 - 14:05",
        )

    def test_aware_near_midnight_shifts_day_in_tehran(self):
        # 2024-03-19 20:30 UTC == 2024-03-20 00:00 Tehran (Nowruz)
        value = datetime(2024, 3, 19, 20, 30, tzinfo=timezone.utc)
        self.assertEqual(jalali(value), "1403/01/01")

    def test_nowruz_morning(self):
        value = datetime(2024, 3, 20, 0, 30, tzinfo=TEHRAN)
        self.assertEqual(jalali(value), "1403/01/01")

    def test_day_before_nowruz(self):
        value = datetime(2024, 3, 19, 23, 30, tzinfo=TEHRAN)
        self.assertEqual(jalali(value), "1402/12/29")

    def test_plain_date(self):
        self.assertEqual(jalali(date(2024, 3, 20)), "1403/01/01")
        self.assertEqual(jalali(date(2024, 3, 19)), "1402/12/29")
