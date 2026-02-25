from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from .models import Vehicle
from .filters import VehicleFilter

def vehicle_list(request):
    queryset = Vehicle.objects.all()

    vehicle_filter = VehicleFilter(request.GET, queryset=queryset)

    context = {
        "filter": vehicle_filter,
        "vehicles": vehicle_filter.qs,
    }

    return render(request, "vehicles/vehicle_list.html", context)


def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, "vehicles/vehicle_detail.html", {
        "vehicle": vehicle
    })