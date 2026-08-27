from order.models import CouponModel


class CouponRepository:
    def get_by_code(self, code: str) -> CouponModel | None:
        try:
            return CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            return None
