from django.shortcuts import render, get_object_or_404
from .models import Vehicle
from django.contrib.auth.decorators import login_required


def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by("-created_at")
    return render(request, "vehicles/vehicle_list.html", {
        "vehicles": vehicles
    })


def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, "vehicles/vehicle_detail.html", {
        "vehicle": vehicle
    })