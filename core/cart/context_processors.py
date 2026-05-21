from .cart import CartSession


def cart_processor(request):
    cart = CartSession(request.session)
    if request.user.is_authenticated:
        cart.ensure_user_cart(request.user)
    return {"cart": cart}