from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from order.messages import CouponMessages
from order.models import CouponModel
from order.services.coupon import CouponService, CouponValidationError

User = get_user_model()


class CouponServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_customer(
            email="customer@example.com",
            password="test-pass-123",
        )
        self.service = CouponService()

    def test_empty_code_raises_not_found(self):
        with self.assertRaises(CouponValidationError) as ctx:
            self.service.get_valid_coupon(code="", user=self.user)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.message, CouponMessages.COUPON_NOT_FOUND)

    def test_unknown_code_raises_not_found(self):
        with self.assertRaises(CouponValidationError) as ctx:
            self.service.get_valid_coupon(code="NOPE", user=self.user)

        self.assertEqual(ctx.exception.status_code, 404)

    def test_valid_coupon_returns_coupon(self):
        coupon = CouponModel.objects.create(
            code="SAVE10",
            discount_percent=10,
            max_limit_usage=5,
        )

        result = self.service.get_valid_coupon(code="SAVE10", user=self.user)

        self.assertEqual(result.pk, coupon.pk)

    def test_expired_coupon_raises(self):
        CouponModel.objects.create(
            code="OLD",
            discount_percent=10,
            expiration_date=timezone.now() - timedelta(days=1),
        )

        with self.assertRaises(CouponValidationError) as ctx:
            self.service.get_valid_coupon(code="OLD", user=self.user)

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.message, CouponMessages.COUPON_EXPIRED)

    def test_already_used_by_user_raises(self):
        coupon = CouponModel.objects.create(
            code="USED",
            discount_percent=10,
            max_limit_usage=5,
        )
        coupon.used_by.add(self.user)

        with self.assertRaises(CouponValidationError) as ctx:
            self.service.get_valid_coupon(code="USED", user=self.user)

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.message, CouponMessages.COUPON_USED_BY_YOU)

    def test_capacity_full_raises(self):
        coupon = CouponModel.objects.create(
            code="FULL",
            discount_percent=10,
            max_limit_usage=1,
        )
        other = User.objects.create_customer(
            email="other@example.com",
            password="test-pass-123",
        )
        coupon.used_by.add(other)

        with self.assertRaises(CouponValidationError) as ctx:
            self.service.get_valid_coupon(code="FULL", user=self.user)

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.message, CouponMessages.COUPON_CAPACITY_IS_FULL)
