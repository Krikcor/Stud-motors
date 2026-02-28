from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied

from vehicles.models import Vehicle
from .forms import ReservationForm
from .models import Reservation

from client.models import Reservation
from django.contrib.auth.decorators import login_required


@login_required
def client_dashboard(request):
    if hasattr(request.user, "profile") and request.user.profile.role != "client":
        raise PermissionDenied

    return render(request, "client/pageclient.html")


@login_required
def reservation_form(request, slug):

    vehicle = get_object_or_404(Vehicle, slug=slug)

    # véhicule déjà réservé
    if vehicle.status == Vehicle.RESERVED:
        return redirect("vehicle_list")

    if request.method == "POST":

        form = ReservationForm(
            request.POST,
            request.FILES
        )

        #  retourner render NORMAL
        # (Django ajoute automatiquement context → assertFormError OK)
        if not form.is_valid():
            return render(
                request,
                "client/reservation_form.html",
                {
                    "form": form,
                    "vehicle": vehicle,
                }
            )

        # bloque double réservation
        if Reservation.objects.filter(
            user=request.user,
            vehicle=vehicle
        ).exists():
            return render(
                request,
                "client/reservation_form.html",
                {
                    "form": form,
                    "vehicle": vehicle,
                }
            )

        reservation = form.save(commit=False)
        reservation.user = request.user
        reservation.vehicle = vehicle
        reservation.save()

        vehicle.status = Vehicle.RESERVED
        vehicle.save()

        return redirect("vehicle_list")

    # GET
    form = ReservationForm()

    return render(
        request,
        "client/reservation_form.html",
        {
            "form": form,
            "vehicle": vehicle,
        }
    )

@login_required
def client_dashboard(request):

    reservations = Reservation.objects.filter(
        client=request.user
    ).order_by("-id")

    return render(
        request,
        "client/dashboard.html",
        {"reservations": reservations}
    )

@login_required
def client_reservation_detail(request, pk):

    reservation = Reservation.objects.get(
        pk=pk,
        client=request.user
    )

    return render(
        request,
        "client/reservation_detail.html",
        {"reservation": reservation}
    )