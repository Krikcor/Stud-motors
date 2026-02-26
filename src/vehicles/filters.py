import django_filters
from django import forms
from .models import Vehicle


class VehicleFilter(django_filters.FilterSet):

    # Prix
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

    # Année min et km max
    min_year = django_filters.NumberFilter(
        field_name="year",
        lookup_expr="gte",
        label="Année min"
    )

    max_mileage = django_filters.NumberFilter(
        field_name="mileage",
        lookup_expr="lte",
        label="Kilométrage max"
    )

    # Masquer les véhicules réservés
    hide_reserved = django_filters.BooleanFilter(
        field_name="status",
        method="filter_hide_reserved",
        label="Masquer les véhicules en cours de réservation",
        widget=forms.CheckboxInput
    )

    # Type de véhicule avec "Tout" au lieu de "---------"
    vehicle_type = django_filters.ChoiceFilter(
        field_name="vehicle_type",
        choices=Vehicle.VEHICLE_TYPE_CHOICES,
        label="Type",
        empty_label="Tout",
        widget=forms.Select
    )

    # Tri
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
        fields = []  # plus besoin de déclarer vehicle_type ici

    # Méthodes de filtrage personnalisées
    def filter_by_order(self, queryset, name, value):
        if value == "price_asc":
            return queryset.order_by("price")
        if value == "price_desc":
            return queryset.order_by("-price")
        return queryset

    def filter_hide_reserved(self, queryset, name, value):
        """
        Si la checkbox est cochée, on exclut les véhicules réservés
        """
        if value:
            return queryset.exclude(status=Vehicle.RESERVED)
        return queryset