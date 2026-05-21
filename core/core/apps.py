from django.apps import AppConfig
from django.utils.translation import activate


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    label = "shop_core"
    verbose_name = "تنظیمات هسته"

    def ready(self):
        activate("fa")
        from core.forms_persian import patch_django_forms, patch_rest_framework_fields

        patch_django_forms()
        patch_rest_framework_fields()
