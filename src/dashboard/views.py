from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from .forms import VehicleForm
from vehicles.models import VehicleImage

from django.http import HttpResponseForbidden
from vehicles.models import Vehicle


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
        # ⚠️ IMPORTANT : ajouter request.FILES
        form = VehicleForm(request.POST, request.FILES)

        if form.is_valid():
            vehicle = form.save()

            # 🔹 Gestion des images secondaires
            secondary_images = request.FILES.getlist("secondary_images")
            for image in secondary_images:
                VehicleImage.objects.create(
                    vehicle=vehicle,
                    image=image
                )

            messages.success(request, "Véhicule ajouté avec succès.")
            return redirect("pro_dashboard")
    else:
        form = VehicleForm()

    return render(
        request,
        "dashboard/create_vehicle.html",
        {"form": form}
    )




@login_required
def delete_vehicle(request):

    # Vérifie seulement que c'est un pro
    if request.user.profile.role != "pro":
        return HttpResponseForbidden()

    # Étape 1 : saisie ID
    if request.method == "POST" and "vehicle_id" in request.POST:
        vehicle_id = request.POST.get("vehicle_id")

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)

            return render(request, "dashboard/confirm_delete.html", {
                "vehicle": vehicle
            })

        except Vehicle.DoesNotExist:
            return render(request, "dashboard/delete_vehicle.html", {
                "error": "Véhicule introuvable."
            })

    # Étape 2 : confirmation
    if request.method == "POST" and "confirm_delete" in request.POST:
        vehicle_id = request.POST.get("confirm_delete")
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)

        vehicle.delete()
        return redirect("pro_dashboard")

    return render(request, "dashboard/delete_vehicle.html")