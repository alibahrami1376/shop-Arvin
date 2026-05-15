from .models import ProductCategoryModel


def shop_categories(request):
    return {
        "shop_categories": ProductCategoryModel.objects.all().order_by("title"),
    }
