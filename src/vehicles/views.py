from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import Http404

from .models import Vehicle
from .filters import VehicleFilter


def vehicle_list(request):
    """
    Liste des véhicules.
    """

    # cache uniquement les véhicules vendus
    queryset = (
        Vehicle.objects
        .exclude(status=Vehicle.SOLD)
        .prefetch_related("images")
    )

    # Filtres
    vehicle_filter = VehicleFilter(request.GET, queryset=queryset)
    vehicles = vehicle_filter.qs

    # Tri
    order_by = request.GET.get("order_by")
    if order_by in ["price", "-price", "year", "-year"]:
        vehicles = vehicles.order_by(order_by)

    # Pagination
    paginator = Paginator(vehicles, 16)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "filter": vehicle_filter,
        "vehicles": page_obj,
        "page_obj": page_obj,
        "current_order": order_by,
        "total_results": vehicles.count(),
    }

    return render(request, "vehicles/vehicle_list.html", context)


def vehicle_detail(request, slug):
    """
    Page détail véhicule.
    """

    vehicle = get_object_or_404(
        Vehicle.objects.prefetch_related("images"),
        slug=slug
    )

    # Empêche accès si vendu
    if vehicle.status == Vehicle.SOLD:
        raise Http404("Vehicle sold")

    # compteur vues
    vehicle.views += 1
    vehicle.save(update_fields=["views"])

    context = {
        "vehicle": vehicle,
        "is_reserved": vehicle.status == Vehicle.RESERVED,
        "is_available": vehicle.status == Vehicle.AVAILABLE,
    }

    return render(request, "vehicles/vehicle_detail.html", context)