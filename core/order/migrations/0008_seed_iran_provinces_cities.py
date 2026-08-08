from django.db import migrations


def seed_locations(apps, schema_editor):
    Province = apps.get_model("order", "Province")
    City = apps.get_model("order", "City")
    from order.iran_locations import IRAN_PROVINCES_CITIES

    for sort_order, (province_name, cities) in enumerate(IRAN_PROVINCES_CITIES.items(), start=1):
        province, _ = Province.objects.get_or_create(
            name=province_name,
            defaults={"is_active": True, "sort_order": sort_order},
        )
        if province.sort_order != sort_order:
            province.sort_order = sort_order
            province.save(update_fields=["sort_order"])
        for city_order, city_name in enumerate(cities, start=1):
            City.objects.get_or_create(
                province=province,
                name=city_name,
                defaults={"is_active": True, "sort_order": city_order},
            )


def unseed_locations(apps, schema_editor):
    Province = apps.get_model("order", "Province")
    City = apps.get_model("order", "City")
    from order.iran_locations import IRAN_PROVINCES_CITIES

    province_names = list(IRAN_PROVINCES_CITIES.keys())
    City.objects.filter(province__name__in=province_names).delete()
    Province.objects.filter(name__in=province_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0007_province_city"),
    ]

    operations = [
        migrations.RunPython(seed_locations, unseed_locations),
    ]
