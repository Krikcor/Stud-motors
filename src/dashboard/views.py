from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from .forms import VehicleForm


@login_required
def pro_dashboard(request):
    """
    Dashboard réservé aux utilisateurs avec le rôle 'pro'.

    """
    if request.user.profile.role != "pro":
        raise PermissionDenied

    return render(request, "dashboard/pro_dashboard.html")


@login_required
def create_vehicle(request):
    """
    Permet à un utilisateur 'pro' d'ajouter un véhicule en base.

    """
    if request.user.profile.role != "pro":
        raise PermissionDenied

    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Véhicule ajouté avec succès.")
            return redirect("pro_dashboard")
    else:
        form = VehicleForm()

    return render(
        request,
        "dashboard/create_vehicle.html",
        {"form": form}
    )