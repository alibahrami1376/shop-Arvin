from datetime import datetime
from zoneinfo import ZoneInfo

from dashboard.admin.forms.blog import BlogPostForm
from dashboard.admin.forms.coupons import CouponForm
from django.test import SimpleTestCase, TestCase
from order.models import CouponModel

from website.jalali_utils import format_jalali_datetime

TEHRAN = ZoneInfo("Asia/Tehran")


class BlogPublishedDateCleanTests(SimpleTestCase):
    def test_empty_becomes_none(self):
        form = BlogPostForm()
        form.cleaned_data = {"published_date": ""}
        self.assertIsNone(form.clean_published_date())
        form.cleaned_data = {"published_date": None}
        self.assertIsNone(form.clean_published_date())

    def test_valid_jalali(self):
        form = BlogPostForm()
        form.cleaned_data = {"published_date": "1403/01/01 - 14:30"}
        parsed = form.clean_published_date()
        self.assertEqual(
            format_jalali_datetime(parsed),
            "1403/01/01 - 14:30",
        )
        self.assertEqual(parsed.tzinfo, TEHRAN)

    def test_invalid_jalali(self):
        form = BlogPostForm()
        form.cleaned_data = {"published_date": "2024-03-20T14:30"}
        with self.assertRaises(Exception) as ctx:
            form.clean_published_date()
        self.assertIn("شمسی", str(ctx.exception))


class CouponExpirationDateFormTests(TestCase):
    def test_empty_expiration_allowed(self):
        form = CouponForm(
            data={
                "code": "TEST10",
                "discount_percent": 10,
                "max_limit_usage": 5,
                "expiration_date": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["expiration_date"])

    def test_valid_jalali_expiration(self):
        form = CouponForm(
            data={
                "code": "TEST20",
                "discount_percent": 20,
                "max_limit_usage": 5,
                "expiration_date": "1403/07/24 - 23:59",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        exp = form.cleaned_data["expiration_date"]
        self.assertIsInstance(exp, datetime)
        self.assertEqual(format_jalali_datetime(exp), "1403/07/24 - 23:59")

    def test_invalid_expiration(self):
        form = CouponForm(
            data={
                "code": "BAD",
                "discount_percent": 5,
                "max_limit_usage": 1,
                "expiration_date": "not-a-date",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("expiration_date", form.errors)

    def test_edit_initial_is_jalali(self):
        coupon = CouponModel.objects.create(
            code="EDITME",
            discount_percent=15,
            max_limit_usage=3,
            expiration_date=datetime(2024, 3, 20, 14, 30, tzinfo=TEHRAN),
        )
        form = CouponForm(instance=coupon)
        self.assertEqual(form.initial["expiration_date"], "1403/01/01 - 14:30")
