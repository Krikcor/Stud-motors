from django import forms
from vehicles.models import Vehicle


class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle
        fields = [
            'brand',
            'model',
            'engine',
            'year',
            'color',
            'mileage',
            'vehicle_type',
            'price',
        ]

        widgets = {
            'vehicle_type': forms.RadioSelect,
        }