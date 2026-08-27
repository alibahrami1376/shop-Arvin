from order.repositories.coupon import CouponRepository
from order.repositories.location import LocationRepository
from order.repositories.order import OrderRepository

__all__ = [
    "OrderRepository",
    "CouponRepository",
    "LocationRepository",
    "order_repo",
    "coupon_repo",
    "location_repo",
]

order_repo = OrderRepository()
coupon_repo = CouponRepository()
location_repo = LocationRepository()
