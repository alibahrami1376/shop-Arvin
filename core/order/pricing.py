"""محاسبه هزینه ارسال، مالیات و مبلغ نهایی سفارش."""

from order.models import CheckoutPricingSettings

# شهرهایی که نرخ «تهران و حومه» برایشان اعمال می‌شود
TEHRAN_AREA_CITIES = frozenset({"تهران", "کرج"})


def is_tehran_area(city: str, state: str = "") -> bool:
    city = (city or "").strip()
    state = (state or "").strip()
    if city in TEHRAN_AREA_CITIES:
        return True
    if state == "تهران" and city:
        return city in TEHRAN_AREA_CITIES or city.startswith("تهران")
    if state == "البرز" and city == "کرج":
        return True
    return False


def calculate_shipping_amount(
    *,
    city: str,
    state: str = "",
    settings: CheckoutPricingSettings | None = None,
) -> int:
    settings = settings or CheckoutPricingSettings.get_solo()
    if not settings.shipping_enabled:
        return 0
    if is_tehran_area(city, state):
        return int(settings.shipping_tehran_amount)
    return int(settings.shipping_province_amount)


def calculate_order_amounts(
    items_subtotal: int,
    *,
    city: str = "",
    state: str = "",
    coupon_percent: int = 0,
    settings: CheckoutPricingSettings | None = None,
) -> dict:
    """
    items_subtotal: جمع قیمت کالاها (قبل از تخفیف، ارسال و مالیات)
    برمی‌گرداند: discount_amount, shipping_amount, tax_amount, grand_total و ...
    """
    settings = settings or CheckoutPricingSettings.get_solo()
    items_subtotal = int(items_subtotal)

    discount_amount = 0
    if coupon_percent > 0:
        discount_amount = round(items_subtotal * coupon_percent / 100)

    after_discount = items_subtotal - discount_amount
    shipping_amount = calculate_shipping_amount(
        city=city, state=state, settings=settings
    )
    tax_amount = settings.calculate_tax_amount(after_discount)
    grand_total = after_discount + shipping_amount + tax_amount

    return {
        "checkout_pricing": settings,
        "subtotal": items_subtotal,
        "discount_amount": discount_amount,
        "shipping_amount": shipping_amount,
        "tax_amount": tax_amount,
        "total_tax": tax_amount,
        "after_discount": after_discount,
        "grand_total": grand_total,
        "total_price": grand_total,
    }


def get_checkout_pricing_context(
    items_subtotal: int,
    *,
    city: str = "",
    state: str = "",
    coupon_percent: int = 0,
) -> dict:
    return calculate_order_amounts(
        items_subtotal,
        city=city,
        state=state,
        coupon_percent=coupon_percent,
    )


def apply_pricing_to_order(order, *, coupon_percent: int | None = None) -> None:
    """مبالغ ارسال و مالیات را روی سفارش ذخیره می‌کند (پس از ثبت اقلام)."""
    items_subtotal = int(order.calculate_total_price())
    order.total_price = items_subtotal

    percent = coupon_percent
    if percent is None and order.coupon_id:
        percent = order.coupon.discount_percent

    amounts = calculate_order_amounts(
        items_subtotal,
        city=order.city,
        state=order.state,
        coupon_percent=percent or 0,
    )
    order.discount_amount = amounts["discount_amount"]
    order.shipping_amount = amounts["shipping_amount"]
    order.tax_amount = amounts["tax_amount"]
    order.save(
        update_fields=[
            "total_price",
            "discount_amount",
            "shipping_amount",
            "tax_amount",
        ]
    )
