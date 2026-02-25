from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Vehicle
from .filters import VehicleFilter
from django.http import Http404

def vehicle_list(request):
    """
    Liste des véhicules.
    - On n'affiche pas les véhicules vendus
    - Les véhicules en cours de réservation restent visibles
    """

    # On exclut les véhicules vendus
    queryset = Vehicle.objects.exclude(status=Vehicle.SOLD)

    # Optimisation ORM (préparation si images multiples)
    queryset = queryset.prefetch_related("images")

    # Application des filtres
    vehicle_filter = VehicleFilter(request.GET, queryset=queryset)
    vehicles = vehicle_filter.qs

    # Tri dynamique
    order_by = request.GET.get("order_by")
    if order_by in ["price", "-price", "year", "-year"]:
        vehicles = vehicles.order_by(order_by)

    # Pagination
    paginator = Paginator(vehicles, 18)  # 18 véhicules par page
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
    Détail d’un véhicule.
    - Empêche l'accès si le véhicule est vendu
    - Incrémente le compteur de vues
    """

    vehicle = get_object_or_404(
        Vehicle.objects.prefetch_related("images"),
        slug=slug
    )

    # Si vendu, afficher page spécifique ou 404
    if vehicle.status == Vehicle.SOLD:
        raise Http404("Vehicle sold")

    # Incrémenter le compteur de vues
    vehicle.views += 1
    vehicle.save(update_fields=["views"])

    context = {
        "vehicle": vehicle,
        "is_reserved": vehicle.status == Vehicle.RESERVED,
        "is_available": vehicle.status == Vehicle.AVAILABLE,
    }

    return render(request, "vehicles/vehicle_detail.html", context)