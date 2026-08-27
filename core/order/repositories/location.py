from order.models import City, Province


class LocationRepository:
    def get_active_provinces(self) -> list[dict]:
        return list(Province.objects.filter(is_active=True).values("id", "name"))

    def get_active_cities_by_province(self) -> dict[int, list[dict]]:
        cities_by_province: dict[int, list[dict]] = {}
        for city in City.objects.filter(
            is_active=True, province__is_active=True
        ).values("id", "name", "province_id"):
            cities_by_province.setdefault(city["province_id"], []).append(
                {"id": city["id"], "name": city["name"]}
            )
        return cities_by_province
