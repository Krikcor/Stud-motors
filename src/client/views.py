from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from vehicles.models import Vehicle
from .forms import ReservationForm
from .models import Reservation

from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.contrib.auth import update_session_auth_hash
from .forms import ClientUpdateForm, OptionalPasswordChangeForm

from django.db import transaction

import logging

logger = logging.getLogger(__name__)


@login_required
def client_dashboard(request):
    """
    Dashboard client : afficher toutes les réservations du client.
    """

    logger.info(f"Accès au dashboard client : {request.user.username}")

    reservations = Reservation.objects.filter(
        user=request.user
    ).order_by("-created_at")

    pending_count = reservations.filter(
        status=Reservation.STATUS_PENDING
    ).count()

    return render(
        request,
        "client/pageclient.html",
        {
            "reservations": reservations,
            "pending_count": pending_count,
            "pending_limit": 4,
        }
    )


@login_required
def reservation_form(request, slug):
    """
    Formulaire de réservation pour un véhicule spécifique.
    """

    logger.info(f"Tentative d'accès au formulaire de réservation par {request.user.username} pour le véhicule {slug}")

    vehicle = get_object_or_404(Vehicle, slug=slug)

    # Seuls les comptes client peuvent réserver
    if request.user.profile.role != "client":
        logger.warning(f"Utilisateur non client a tenté de réserver : {request.user.username}")
        raise PermissionDenied("Seuls les clients peuvent effectuer une réservation.")

    # Limite de réservations en attente
    pending_count = Reservation.objects.filter(
        user=request.user,
        status=Reservation.STATUS_PENDING
    ).count()

    if pending_count >= 4:
        logger.warning(f"Limite de réservations atteinte pour {request.user.username}")
        return render(
            request,
            "client/reservation_limit.html",
            {"limit": 4}
        )

    # Bloquer si le véhicule est vendu
    if vehicle.status == Vehicle.SOLD:
        logger.warning(f"Tentative de réservation d'un véhicule vendu : {vehicle.slug}")
        return redirect("vehicle_list")

    # Bloquer si déjà en cours de réservation
    if vehicle.status == Vehicle.RESERVED:
        logger.warning(f"Tentative de réservation d'un véhicule déjà réservé : {vehicle.slug}")
        return redirect("vehicle_list")

    if request.method == "POST":

        logger.info(f"Soumission du formulaire de réservation par {request.user.username}")

        form = ReservationForm(request.POST, request.FILES)

        if not form.is_valid():
            logger.warning("Formulaire de réservation invalide")
            return render(
                request,
                "client/reservation_form.html",
                {"form": form, "vehicle": vehicle}
            )

        # Empêcher double réservation par le même utilisateur
        if Reservation.objects.filter(user=request.user, vehicle=vehicle).exists():
            logger.warning(f"Tentative de double réservation par {request.user.username} pour {vehicle.slug}")
            return render(
                request,
                "client/reservation_form.html",
                {"form": form, "vehicle": vehicle}
            )

        # Transaction atomique pour éviter les réservations simultanées
        with transaction.atomic():

            # Recharge l'état du véhicule depuis la base
            vehicle.refresh_from_db()

            # Si quelqu'un l'a réservé entre temps
            if vehicle.status != Vehicle.AVAILABLE:
                logger.warning(f"Véhicule réservé entre temps : {vehicle.slug}")
                form.add_error(None, "Désolé, ce véhicule vient d'être réservé, veuillez retourner vers la page de vehicule via la barre de navigation.")
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

            logger.info(f"Réservation créée par {request.user.username} pour le véhicule {vehicle.slug}")

            # Passage en "en cours"
            vehicle.status = Vehicle.RESERVED
            vehicle.save()

        return redirect("reservation_success")

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

    logger.info(f"Consultation du détail de réservation {pk} par {request.user.username}")

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

        logger.warning(f"Suppression du compte client : {user.username}")

        # Récupérer les réservations pending
        pending_reservations = Reservation.objects.filter(
            user=user,
            status=Reservation.STATUS_PENDING
        )

        for reservation in pending_reservations:
            vehicle = reservation.vehicle

            # Supprimer la réservation
            reservation.delete()

            logger.info(f"Suppression d'une réservation pending pour {user.username}")

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

        logger.info("Compte client supprimé avec succès")

        return redirect("vehicle_list")

    return redirect("client_dashboard")


@login_required
def edit_profile(request):

    if request.user.profile.role != "client":
        logger.warning(f"Accès refusé à edit_profile pour {request.user.username}")
        return redirect("vehicle_list")

    if request.method == "POST":

        logger.info(f"Tentative de modification du profil pour {request.user.username}")

        form = ClientUpdateForm(request.POST, instance=request.user)
        password_form = OptionalPasswordChangeForm(request.POST)

        if form.is_valid() and password_form.is_valid():

            user = form.save()

            new_password = password_form.cleaned_data.get("new_password1")

            if new_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)

                logger.info(f"Mot de passe modifié pour {request.user.username}")

            logger.info(f"Profil mis à jour pour {request.user.username}")

            return redirect("client_dashboard")

    else:
        form = ClientUpdateForm(instance=request.user)
        password_form = OptionalPasswordChangeForm()

    return render(request, "client/edit_profile.html", {
        "form": form,
        "password_form": password_form
    })


@login_required
def reservation_success(request):
    """
    Page de confirmation après création d'une réservation.
    """

    logger.info(f"Affichage de la page de succès de réservation pour {request.user.username}")

    return render(request, "client/success.html")