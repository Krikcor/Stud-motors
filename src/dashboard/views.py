from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from .forms import VehicleForm
from vehicles.models import VehicleImage

from django.http import HttpResponseForbidden
from vehicles.models import Vehicle

from django.shortcuts import render



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




@login_required
def modify_vehicle(request):

    if request.user.profile.role != "pro":
        return HttpResponseForbidden()

    # Recherche par ID
    if request.method == "POST" and "vehicle_id" in request.POST:
        vehicle_id = request.POST.get("vehicle_id")

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            return render(request, "dashboard/modif_vehicle.html", {
                "vehicle": vehicle
            })
        except Vehicle.DoesNotExist:
            return render(request, "dashboard/modif_vehicle.html", {
                "error": "Véhicule introuvable."
            })

    # Sauvegarde des modifications
    if request.method == "POST" and "save_modifications" in request.POST:
        vehicle_id = request.POST.get("save_modifications")
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)

        vehicle.brand = request.POST.get("brand")
        vehicle.model = request.POST.get("model")
        vehicle.engine = request.POST.get("engine")
        vehicle.year = request.POST.get("year")
        vehicle.color = request.POST.get("color")
        vehicle.mileage = request.POST.get("mileage")
        vehicle.vehicle_type = request.POST.get("vehicle_type")
        vehicle.price = request.POST.get("price")

        vehicle.save()

        return redirect("pro_dashboard")

    return render(request, "dashboard/modif_vehicle.html")


@login_required
def list_vehicle(request):

    if request.user.profile.role != "pro":
        return HttpResponseForbidden()

    vehicles = Vehicle.objects.all().order_by("-created_at")

    return render(request, "dashboard/list_vehicle.html", {
        "vehicles": vehicles
    })

from client.models import Reservation
from vehicles.models import Vehicle

@login_required
def pro_reservations(request):

    if request.user.profile.role != "pro":
        return HttpResponseForbidden()

    reservations = Reservation.objects.select_related(
        "user",
        "vehicle"
    ).order_by("-created_at")

    return render(
        request,
        "dashboard/pro_reservations.html",
        {"reservations": reservations}
    )

@login_required
def reservation_detail(request, pk):

    if request.user.profile.role != "pro":
        return HttpResponseForbidden()

    reservation = get_object_or_404(Reservation, pk=pk)

    return render(
        request,
        "dashboard/reservation_detail.html",
        {"reservation": reservation}
    )

@login_required
def reservation_decision(request, pk, decision):

    if request.user.profile.role != "pro":
        return HttpResponseForbidden()

    reservation = get_object_or_404(Reservation, pk=pk)

    if decision == "approve":
        reservation.status = Reservation.STATUS_APPROVED
        reservation.vehicle.status = Vehicle.SOLD

    elif decision == "refuse":
        reservation.status = Reservation.STATUS_REFUSED
        reservation.vehicle.status = Vehicle.AVAILABLE

    reservation.vehicle.save()
    reservation.save()

    return redirect("pro_reservations")

