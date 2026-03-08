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
            'vehicle_type': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # on force les choix du modèle
        self.fields["vehicle_type"].choices = Vehicle.VEHICLE_TYPE_CHOICES