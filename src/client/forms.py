from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):

    class Meta:
        model = Reservation
        fields = [
            "phone",
            "address",
            "city",
            "postal_code",
            "country",
            "driver_license",
            "accepted_terms",
            "accepted_gdpr",
        ]