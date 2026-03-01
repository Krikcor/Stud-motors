from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from vehicles.models import Vehicle
from .forms import ReservationForm
from .models import Reservation


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

    # Bloquer si le véhicule est déjà réservé
    if vehicle.status == Vehicle.RESERVED:
        return redirect("vehicle_list")

    if request.method == "POST":
        form = ReservationForm(request.POST, request.FILES)

        # Si le formulaire n'est pas valide, on le réaffiche
        if not form.is_valid():
            return render(
                request,
                "client/reservation_form.html",
                {"form": form, "vehicle": vehicle}
            )

        # Empêcher la double réservation du même véhicule par le même utilisateur
        if Reservation.objects.filter(user=request.user, vehicle=vehicle).exists():
            return render(
                request,
                "client/reservation_form.html",
                {"form": form, "vehicle": vehicle}
            )

        # Création de la réservation
        reservation = form.save(commit=False)
        reservation.user = request.user
        reservation.vehicle = vehicle
        reservation.save()

        # Mettre le véhicule en statut réservé
        vehicle.status = Vehicle.RESERVED
        vehicle.save()

        return redirect("vehicle_list")

    # GET : affichage du formulaire
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