from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .forms import VehicleForm
from vehicles.models import VehicleImage
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils import timezone
from client.models import Reservation
from vehicles.models import Vehicle
from vehicles.filters import VehicleFilter
import logging

logger = logging.getLogger(__name__)


@login_required
def pro_dashboard(request):
    """
    Dashboard réservé aux utilisateurs avec le rôle 'pro'.
    """
    logger.info(f"Accès au dashboard pro par {request.user.username}")

    if request.user.profile.role != "pro":
        logger.warning(f"Tentative d'accès non autorisé au dashboard pro par {request.user.username}")
        raise PermissionDenied

    return render(request, "dashboard/pro_dashboard.html")


@login_required
def create_vehicle(request):
    """
    Permet à un utilisateur 'pro' d'ajouter un véhicule en base.
    """
    logger.info(f"{request.user.username} accède à la création de véhicule")

    if request.user.profile.role != "pro":
        logger.warning(f"Tentative création véhicule non autorisée par {request.user.username}")
        raise PermissionDenied

    if request.method == "POST":
        # ajouter request.FILES
        form = VehicleForm(request.POST, request.FILES)

        if form.is_valid():
            vehicle = form.save()
            logger.info(f"Véhicule créé ID={vehicle.id} par {request.user.username}")

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
            logger.warning(f"Formulaire véhicule invalide soumis par {request.user.username}")

    else:
        form = VehicleForm()

    return render(
        request,
        "dashboard/create_vehicle.html",
        {"form": form}
    )


@login_required
def delete_vehicle(request):

    if request.user.profile.role != "pro":
        return HttpResponseForbidden()

    # 1. QUERYSET + FILTRE (AJOUT SAFE)
    queryset = Vehicle.objects.all().order_by("-created_at")
    vehicle_filter = VehicleFilter(request.GET, queryset=queryset)
    vehicles = vehicle_filter.qs

    vehicle = None
    error = None

    # 2. Sélection via GET (nouvelle UI liste cliquable)
    vehicle_id = request.GET.get("id")

    if vehicle_id:
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            error = "Véhicule introuvable."

    # 3. Sélection via POST (ancienne UI / tests)
    if request.method == "POST" and "vehicle_id" in request.POST:
        vehicle_id = request.POST.get("vehicle_id")

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)

            return render(request, "dashboard/confirm_delete.html", {
                "vehicle": vehicle
            })

        except Vehicle.DoesNotExist:
            return render(request, "dashboard/delete_vehicle.html", {
                "vehicles": vehicles,
                "error": "Véhicule introuvable.",
                "filter": vehicle_filter
            })

    # 4. Confirmation suppression
    if request.method == "POST" and "confirm_delete" in request.POST:
        vehicle_id = request.POST.get("confirm_delete")
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)

        vehicle.delete()
        return redirect("pro_dashboard")

    # 5. Rendu final (avec filtres)
    return render(request, "dashboard/delete_vehicle.html", {
        "vehicles": vehicles,
        "vehicle": vehicle,
        "error": error,
        "filter": vehicle_filter
    })




@login_required
def modify_vehicle(request):

    logger.info(f"{request.user.username} accède à la modification de véhicule")

    # Sécurité rôle
    if request.user.profile.role != "pro":
        logger.warning(
            f"Tentative modification véhicule non autorisée par {request.user.username}"
        )
        return HttpResponseForbidden()

    # 1. QUERYSET DE BASE
    queryset = Vehicle.objects.all().order_by("-created_at")

    # 2. FILTRE (AJOUT SAFE)
    vehicle_filter = VehicleFilter(request.GET, queryset=queryset)
    vehicles = vehicle_filter.qs

    vehicle = None
    error = None

    # 3. Sélection via liste (GET)
    vehicle_id = request.GET.get("id")

    if vehicle_id:
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            error = "Véhicule introuvable"

    # 4. Recherche via POST (compat ancienne UI)
    if request.method == "POST" and "vehicle_id" in request.POST:
        vehicle_id = request.POST.get("vehicle_id")

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            error = "Véhicule introuvable"

    # 5. Sauvegarde des modifications
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

        logger.info(
            f"Véhicule ID={vehicle_id} modifié par {request.user.username}"
        )

        return redirect("list_vehicle")

    # 6. Rendu final
    return render(request, "dashboard/modif_vehicle.html", {
        "vehicles": vehicles,
        "vehicle": vehicle,
        "error": error,
        "filter": vehicle_filter  # ← indispensable pour le template
    })


@login_required
def list_vehicle(request):

    logger.info(f"{request.user.username} consulte la liste des véhicules")

    if request.user.profile.role != "pro":
        logger.warning(f"Tentative accès liste véhicules non autorisée par {request.user.username}")
        return HttpResponseForbidden()

    vehicles = Vehicle.objects.all().order_by("-created_at")

    return render(request, "dashboard/list_vehicle.html", {
        "vehicles": vehicles
    })


@login_required
def pro_reservations(request):

    logger.info(f"{request.user.username} consulte les réservations")

    if request.user.profile.role != "pro":
        logger.warning(f"Tentative accès réservations non autorisée par {request.user.username}")
        return HttpResponseForbidden()

    reservations = Reservation.objects.select_related(
        "user",
        "vehicle",
        "validated_by"
    ).order_by("-created_at")

    return render(
        request,
        "dashboard/pro_reservations.html",
        {"reservations": reservations}
    )


@login_required
def reservation_detail(request, pk):

    logger.info(f"{request.user.username} consulte le détail réservation ID={pk}")

    if request.user.profile.role != "pro":
        logger.warning(f"Tentative accès détail réservation non autorisée par {request.user.username}")
        return HttpResponseForbidden()

    reservation = get_object_or_404(Reservation, pk=pk)

    return render(
        request,
        "dashboard/reservation_detail.html",
        {"reservation": reservation}
    )


@login_required
def reservation_decision(request, pk, decision):

    logger.info(f"{request.user.username} prend décision {decision} sur réservation ID={pk}")

    if request.user.profile.role != "pro":
        logger.warning(f"Tentative décision réservation non autorisée par {request.user.username}")
        return HttpResponseForbidden()

    reservation = get_object_or_404(Reservation, pk=pk)

    if reservation.status != Reservation.STATUS_PENDING:
        logger.warning(f"Tentative décision sur réservation non pending ID={pk}")
        return redirect("pro_reservations")

    if decision == "approve":
        reservation.status = Reservation.STATUS_APPROVED
        reservation.vehicle.status = Vehicle.SOLD
        logger.info(f"Réservation ID={pk} approuvée par {request.user.username}")

    elif decision == "refuse":
        reservation.status = Reservation.STATUS_REFUSED
        reservation.vehicle.status = Vehicle.AVAILABLE
        logger.info(f"Réservation ID={pk} refusée par {request.user.username}")

    reservation.validated_by = request.user
    reservation.validated_at = timezone.now()

    reservation.vehicle.save()
    reservation.save()

    return redirect("pro_reservations")


@login_required
def change_vehicle_type(request):

    logger.info(f"{request.user.username} accède au changement de type véhicule")

    if request.user.profile.role != "pro":
        logger.warning(f"Tentative modification type véhicule non autorisée par {request.user.username}")
        return HttpResponseForbidden()

    # Étape 1 : recherche par ID
    if request.method == "POST" and "vehicle_id" in request.POST:
        vehicle_id = request.POST.get("vehicle_id")

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)

            logger.info(f"Changement de type demandé pour véhicule ID={vehicle_id}")

            return render(
                request,
                "dashboard/change_vehicle_type.html",
                {"vehicle": vehicle}
            )

        except Vehicle.DoesNotExist:
            logger.warning(f"Changement type demandé pour véhicule inexistant ID={vehicle_id}")
            return render(
                request,
                "dashboard/change_vehicle_type.html",
                {"error": "Véhicule introuvable."}
            )

    # modification du type
    if request.method == "POST" and "save_type" in request.POST:
        vehicle_id = request.POST.get("save_type")
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)

        if vehicle.status != Vehicle.AVAILABLE:
            return render(
                request,
                "dashboard/change_vehicle_type.html",
                {
                    "vehicle": vehicle,
                    "error": "Impossible de modifier un véhicule réservé ou vendu."
                }
            )

        new_type = request.POST.get("vehicle_type")
        new_price = request.POST.get("price")

        if new_type in [Vehicle.PURCHASE, Vehicle.RENTAL]:

            vehicle.vehicle_type = new_type

            if new_price:
                vehicle.price = new_price

            vehicle.save()

            messages.success(request, "Type et prix du véhicule modifiés avec succès.")
            return redirect("pro_dashboard")

    return render(request, "dashboard/change_vehicle_type.html")