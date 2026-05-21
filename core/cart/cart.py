from shop.models import ProductModel, ProductStatusType
from cart.models import CartModel, CartItemModel


class CartSession:
    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault("cart", {"items": []})
        self._normalize_item_product_ids()

    def _normalize_item_product_ids(self):
        for item in self._cart.get("items", []):
            if "product_id" in item:
                item["product_id"] = str(item["product_id"])

    @staticmethod
    def _pid(product_id):
        return str(product_id)

    def _get_db_cart_map(self, user):
        cart, _ = CartModel.objects.get_or_create(user=user)
        db_map = {}
        for cart_item in CartItemModel.objects.filter(cart=cart).select_related("product"):
            if cart_item.product.status == ProductStatusType.publish.value:
                db_map[str(cart_item.product.id)] = cart_item.quantity
        return db_map

    def update_product_quantity(self, product_id, quantity):
        product_id = self._pid(product_id)
        for item in self._cart["items"]:
            if product_id == item["product_id"]:
                item["quantity"] = int(quantity)
                break
        else:
            return
        self.save()

    def remove_product(self, product_id):
        product_id = self._pid(product_id)
        for item in self._cart["items"]:
            if product_id == item["product_id"]:
                self._cart["items"].remove(item)
                break
        else:
            return
        self.save()

    def add_product(self, product_id):
        product_id = self._pid(product_id)
        for item in self._cart["items"]:
            if product_id == item["product_id"]:
                item["quantity"] += 1
                break
        else:
            new_item = {"product_id": product_id, "quantity": 1}
            self._cart["items"].append(new_item)
        self.save()

    def clear(self):
        self._cart = self.session["cart"] = {"items": []}
        self.save()

    def get_cart_dict(self):
        return self._cart

    def get_cart_items(self):
        for item in self._cart["items"]:
            product_obj = ProductModel.objects.get(
                id=item["product_id"], status=ProductStatusType.publish.value
            )
            item.update(
                {
                    "product_obj": product_obj,
                    "total_price": item["quantity"] * product_obj.get_price(),
                }
            )

        return self._cart["items"]

    def get_total_payment_amount(self):
        return sum(item["total_price"] for item in self.get_cart_items())

    def get_total_quantity(self):
        return sum(item["quantity"] for item in self._cart["items"])

    def get_total_price(self):
        """جمع مبلغ سبد برای نمایش در هدر (بدون وابستگی به get_cart_items)."""
        total = 0
        for item in self._cart["items"]:
            try:
                product = ProductModel.objects.get(
                    id=item["product_id"], status=ProductStatusType.publish.value
                )
                total += item["quantity"] * product.get_price()
            except (ProductModel.DoesNotExist, ValueError):
                continue
        return total

    def save(self):
        self.session.modified = True

    def ensure_user_cart(self, user):
        """
        اگر کاربر لاگین است ولی سشن خالی است، سبد را از دیتابیس بازیابی می‌کند.
        (پشتیبان برای زمانی که سیگنال ورود اجرا نشده باشد)
        """
        if self._cart["items"]:
            return
        db_map = self._get_db_cart_map(user)
        if not db_map:
            return
        self._cart["items"] = [
            {"product_id": pid, "quantity": qty} for pid, qty in db_map.items()
        ]
        self.save()

    def merge_carts(self, user):
        """پس از ورود: ادغام سبد مهمان (سشن) با سبد ذخیره‌شده در دیتابیس."""
        db_map = self._get_db_cart_map(user)
        session_map = {item["product_id"]: item["quantity"] for item in self._cart["items"]}

        if not session_map and not db_map:
            return

        merged = dict(db_map)
        for pid, qty in session_map.items():
            if pid in merged:
                merged[pid] += qty
            else:
                merged[pid] = qty

        self._cart["items"] = [
            {"product_id": pid, "quantity": qty} for pid, qty in merged.items()
        ]
        self.persist_to_db(user)
        self.save()

    def persist_to_db(self, user):
        """محتوای سشن را در دیتابیس ذخیره می‌کند (منبع حقیقت = سشن)."""
        cart, _ = CartModel.objects.get_or_create(user=user)
        merged_ids = []

        for item in self._cart["items"]:
            try:
                product_obj = ProductModel.objects.get(
                    id=item["product_id"], status=ProductStatusType.publish.value
                )
            except (ProductModel.DoesNotExist, ValueError, TypeError):
                continue

            cart_item, _ = CartItemModel.objects.get_or_create(
                cart=cart, product=product_obj
            )
            cart_item.quantity = item["quantity"]
            cart_item.save()
            merged_ids.append(str(product_obj.id))

        CartItemModel.objects.filter(cart=cart).exclude(
            product__id__in=merged_ids
        ).delete()
        self.save()

    # سازگاری با کد قبلی
    def sync_cart_items_from_db(self, user):
        self.merge_carts(user)

    def merge_session_cart_in_db(self, user):
        self.persist_to_db(user)
