from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from vehicles.models import Vehicle
from .forms import ReservationForm
from .models import Reservation

from django.contrib import messages
from django.contrib.auth import logout

@login_required
def client_dashboard(request):
    """
    Dashboard client : afficher toutes les réservations du client.
    """
    reservations = Reservation.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "client/pageclient.html",
        {"reservations": reservations}
    )


@login_required
def reservation_form(request, slug):
    """
    Formulaire de réservation pour un véhicule spécifique.
    """

    vehicle = get_object_or_404(Vehicle, slug=slug)

    # Seuls les comptes client peuvent réserver
    if request.user.profile.role != "client":
        raise PermissionDenied("Seuls les clients peuvent effectuer une réservation.")

    # Bloquer si le véhicule est vendu
    if vehicle.status == Vehicle.SOLD:
        return redirect("vehicle_list")

    # Bloquer si déjà en cours de réservation
    if vehicle.status == Vehicle.RESERVED:
        return redirect("vehicle_list")

    if request.method == "POST":
        form = ReservationForm(request.POST, request.FILES)

        if not form.is_valid():
            return render(
                request,
                "client/reservation_form.html",
                {"form": form, "vehicle": vehicle}
            )

        # Empêcher double réservation par le même utilisateur
        if Reservation.objects.filter(user=request.user, vehicle=vehicle).exists():
            return render(
                request,
                "client/reservation_form.html",
                {"form": form, "vehicle": vehicle}
            )

        # Création réservation
        reservation = form.save(commit=False)
        reservation.user = request.user
        reservation.vehicle = vehicle
        reservation.save()

        # Passage en "en cours"
        vehicle.status = Vehicle.RESERVED
        vehicle.save()

        return redirect("vehicle_list")

    # GET
    form = ReservationForm()
    return render(
        request,
        "client/reservation_form.html",
        {"form": form, "vehicle": vehicle}
    )


@login_required
def client_reservation_detail(request, pk):
    """
    Affiche le détail d'une réservation spécifique pour le client.
    """
    reservation = get_object_or_404(
        Reservation,
        pk=pk,
        user=request.user
    )

    return render(
        request,
        "client/reservation_detail.html",
        {"reservation": reservation}
    )

@login_required
def delete_account(request):

    if request.method == "POST":

        user = request.user

        # Récupérer les réservations pending
        pending_reservations = Reservation.objects.filter(
            user=user,
            status=Reservation.STATUS_PENDING
        )

        for reservation in pending_reservations:
            vehicle = reservation.vehicle

            # Supprimer la réservation
            reservation.delete()

            # Si le véhicule était réservé → le remettre disponible
            if vehicle.status == Vehicle.RESERVED:
                vehicle.status = Vehicle.AVAILABLE
                vehicle.save()

        # Supprimer les réservations refusées
        Reservation.objects.filter(
            user=user,
            status=Reservation.STATUS_REFUSED
        ).delete()

        # Détacher les réservations approved
        Reservation.objects.filter(
            user=user,
            status=Reservation.STATUS_APPROVED
        ).update(user=None)

        logout(request)
        user.delete()

        return redirect("vehicle_list")

    return redirect("client_dashboard")