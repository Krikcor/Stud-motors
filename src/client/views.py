from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from vehicles.models import Vehicle
from .forms import ReservationForm
from django.contrib import messages


@login_required
def client_dashboard(request):
    if hasattr(request.user, 'profile') and request.user.profile.role != 'client':
        raise PermissionDenied
    return render(request, 'client/pageclient.html')


@login_required
def reservation_form(request, slug):

    vehicle = get_object_or_404(Vehicle, slug=slug)

    if vehicle.status == Vehicle.RESERVED:
        return redirect("vehicle_list")

    if request.method == "POST":
        form = ReservationForm(request.POST, request.FILES)

        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.vehicle = vehicle
            reservation.save()

            vehicle.status = Vehicle.RESERVED
            vehicle.save()

            return redirect("vehicle_list")

    else:
        form = ReservationForm()

    return render(request, "client/reservation_form.html", {
        "form": form,
        "vehicle": vehicle
    })