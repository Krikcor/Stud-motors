import django_filters
from .models import Vehicle


class VehicleFilter(django_filters.FilterSet):

    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Prix minimum"
    )

    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Prix maximum"
    )

    order_by = django_filters.ChoiceFilter(
        label="Trier par",
        method="filter_by_order",
        choices=(
            ("price_asc", "Prix croissant"),
            ("price_desc", "Prix décroissant"),
        )
    )

    class Meta:
        model = Vehicle
        fields = {
            "vehicle_type": ["exact"],
            "year": ["exact"],
        }

    def filter_by_order(self, queryset, name, value):
        if value == "price_asc":
            return queryset.order_by("price")
        if value == "price_desc":
            return queryset.order_by("-price")
        return queryset