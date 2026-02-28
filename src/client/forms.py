from django import forms
from .models import Reservation


class ReservationForm(forms.ModelForm):

    accepted_terms = forms.BooleanField(
        required=True,
        error_messages={
            "required": "Vous devez accepter les conditions générales."
        }
    )

    accepted_gdpr = forms.BooleanField(
        required=True,
        error_messages={
            "required": "Vous devez accepter la politique de confidentialité."
        }
    )

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

    def clean_driver_license(self):
        file = self.cleaned_data.get("driver_license")

        if not file:
            raise forms.ValidationError(
                "Le permis de conduire est obligatoire."
            )

        allowed_extensions = [".pdf", ".jpg", ".jpeg"]
        filename = file.name.lower()

        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError(
                "Seuls les fichiers PDF, JPG ou JPEG sont acceptés."
            )

        max_size = 5 * 1024 * 1024  # 5MB

        if file.size > max_size:
            raise forms.ValidationError(
                "Le fichier ne doit pas dépasser 5MB."
            )

        return file