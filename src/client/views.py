from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from vehicles.models import Vehicle
from .forms import ReservationForm  # ton formulaire de réservation dans client/forms.py


@login_required
def client_dashboard(request):
    if request.user.profile.role != 'client':
        raise PermissionDenied

    return render(request, 'client/pageclient.html')


@login_required
def reservation_create(request, vehicle_slug):
    """
    Vue principale pour créer une réservation depuis la page véhicule.
    Gère la logique complète : formulaire, statut du véhicule et redirection.
    """
    vehicle = get_object_or_404(Vehicle, slug=vehicle_slug)

    if vehicle.status != Vehicle.AVAILABLE:
        # Si le véhicule n'est pas disponible
        return redirect('vehicle_list')

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.vehicle = vehicle
            reservation.save()

            # Marquer véhicule comme réservé
            vehicle.status = Vehicle.RESERVED
            vehicle.save()

            return redirect('client_dashboard')
    else:
        form = ReservationForm()

    return render(request, 'client/reservation_form.html', {'form': form, 'vehicle': vehicle})


@login_required
def reservation_form(request, slug):
    """
    Vue alternative plus simple pour tester le formulaire de réservation.
    Gère juste le POST et la sauvegarde, affiche success si validé.
    """
    vehicle = get_object_or_404(Vehicle, slug=slug)
    form = ReservationForm(request.POST or None)
    if form.is_valid():
        reservation = form.save(commit=False)
        reservation.user = request.user  # utiliser user pour cohérence
        reservation.vehicle = vehicle
        reservation.save()

        # statut du véhicule à "en cours de réservation"
        vehicle.status = Vehicle.RESERVED
        vehicle.save()

        return render(request, 'client/reservation_success.html', {'vehicle': vehicle})

    return render(request, 'client/reservation_form.html', {'form': form, 'vehicle': vehicle})