from core.caching import get_shop_categories


def shop_categories(request):
    return {
        "shop_categories": get_shop_categories(),
    }
