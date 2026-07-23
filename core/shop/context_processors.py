from django.db.models import Prefetch

from .models import ProductCategoryModel


def shop_categories(request):
    children_qs = ProductCategoryModel.objects.order_by("title")
    return {
        "shop_categories": ProductCategoryModel.objects.filter(parent__isnull=True)
        .prefetch_related(Prefetch("children", queryset=children_qs))
        .order_by("id"),
    }
