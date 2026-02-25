from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Vehicle
from .filters import VehicleFilter


def vehicle_list(request):
    queryset = Vehicle.objects.all()

    # Application des filtres
    vehicle_filter = VehicleFilter(request.GET, queryset=queryset)
    vehicles = vehicle_filter.qs

    # Gestion du tri dynamique
    order_by = request.GET.get("order_by")

    if order_by in ["price", "-price"]:
        vehicles = vehicles.order_by(order_by)

    # Pagination
    paginator = Paginator(vehicles, 18)  # 18 cards par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "filter": vehicle_filter,
        "vehicles": page_obj,  # utilisé dans le template
        "page_obj": page_obj,
        "current_order": order_by,  # utile si tu veux garder le tri sélectionné dans le template
    }

    return render(request, "vehicles/vehicle_list.html", context)


def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, "vehicles/vehicle_detail.html", {
        "vehicle": vehicle
    })