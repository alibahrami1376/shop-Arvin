from django.utils import timezone

from order.messages import CouponMessages
from order.repositories import coupon_repo


class CouponValidationError(Exception):
    def __init__(self, message: str, *, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class CouponService:
    def __init__(self, repository=None):
        self.repo = repository or coupon_repo

    def get_valid_coupon(self, *, code: str, user):
        if not code:
            raise CouponValidationError(
                CouponMessages.COUPON_NOT_FOUND, status_code=404
            )

        coupon = self.repo.get_by_code(code)
        if coupon is None:
            raise CouponValidationError(
                CouponMessages.COUPON_NOT_FOUND, status_code=404
            )

        if coupon.used_by.count() >= coupon.max_limit_usage:
            raise CouponValidationError(
                CouponMessages.COUPON_CAPACITY_IS_FULL,
                status_code=403,
            )

        if coupon.expiration_date and coupon.expiration_date < timezone.now():
            raise CouponValidationError(CouponMessages.COUPON_EXPIRED, status_code=403)

        if user in coupon.used_by.all():
            raise CouponValidationError(
                CouponMessages.COUPON_USED_BY_YOU,
                status_code=403,
            )

        return coupon
