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

    class Meta:
        model = Vehicle
        fields = {
            "vehicle_type": ["exact"],
            "year": ["exact"],
        }