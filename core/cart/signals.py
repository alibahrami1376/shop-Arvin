from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .cart import CartSession


@receiver(user_logged_in)
def restore_cart_on_login(sender, user, request, **kwargs):
    cart = CartSession(request.session)
    cart.merge_carts(user)


@receiver(user_logged_out)
def save_cart_on_logout(sender, user, request, **kwargs):
    if user and getattr(user, "is_authenticated", False):
        cart = CartSession(request.session)
        if cart.get_cart_dict().get("items"):
            cart.persist_to_db(user)
