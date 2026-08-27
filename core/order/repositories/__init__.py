from order.repositories.coupon import CouponRepository
from order.repositories.order import OrderRepository

__all__ = ["OrderRepository", "CouponRepository", "order_repo", "coupon_repo"]

order_repo = OrderRepository()
coupon_repo = CouponRepository()
