from django import forms
from vehicles.models import Vehicle


class VehicleForm(forms.ModelForm):

    secondary_images = forms.FileField(required=False)

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
            'main_image',
        ]

        widgets = {
            'vehicle_type': forms.RadioSelect,
        }