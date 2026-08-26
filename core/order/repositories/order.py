from order.models import OrderItemModel, OrderModel
from order.shipping import ShippingMethodType


class OrderRepository:
    def create(
        self,
        *,
        user,
        province,
        city,
        freight_notes: str,
    ) -> OrderModel:
        return OrderModel.objects.create(
            user=user,
            shipping_method=ShippingMethodType.freight.value,
            state=province.name,
            city=city.name,
            address="-",
            zip_code="-",
            freight_notes=freight_notes,
        )

    def create_items(self, *, order: OrderModel, cart) -> None:
        for item in cart.cart_items.all():
            OrderItemModel.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.get_price(),
            )

    def get_by_tracking_code(self, code: str) -> OrderModel | None:
        return (
            OrderModel.objects.filter(tracking_code=code)
            .select_related("payment")
            .prefetch_related("order_items__product")
            .first()
        )
