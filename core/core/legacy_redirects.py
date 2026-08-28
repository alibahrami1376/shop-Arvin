"""301 redirects for legacy demo-theme .html URLs still linked or indexed."""

from django.shortcuts import redirect
from django.urls import reverse


def legacy_cart_html_redirect(request):
    return redirect(reverse("cart:cart-summary"), permanent=True)


def legacy_product_overview_redirect(request):
    return redirect(reverse("shop:product-grid"), permanent=True)
