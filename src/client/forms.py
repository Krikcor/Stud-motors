from django import forms
from .models import Reservation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class ReservationForm(forms.ModelForm):

    # Options de location → affichage en cases à cocher
    rental_options = forms.MultipleChoiceField(
        choices=Reservation.RENTAL_OPTIONS,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

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
            "identity_document",
            "proof_of_address",
            "rental_options",
            "accepted_terms",
            "accepted_gdpr",
        ]
        labels = {
            "phone": "Téléphone",
            "address": "Adresse",
            "city": "Ville",
            "postal_code": "Code postal",
            "country": "Pays",
            "driver_license": "Permis de conduire",
            "identity_document": "Pièce d'identité",
            "proof_of_address": "Justificatif de domicile",
            "rental_options": "Options de location",
            "accepted_terms": "J'accepte les conditions générales",
            "accepted_gdpr": "J'accepte la politique de confidentialité (RGPD)",
        }

        widgets = {
            "phone": forms.TextInput(attrs={
                "placeholder": "Ex : 0612345678"
            }),
            "address": forms.TextInput(attrs={
                "placeholder": "Votre adresse complète"
            }),
            "city": forms.TextInput(attrs={
                "placeholder": "Votre ville"
            }),
            "postal_code": forms.TextInput(attrs={
                "placeholder": "Ex : 75000"
            }),
            "country": forms.TextInput(attrs={
                "placeholder": "Votre pays"
            }),
            "driver_license": forms.ClearableFileInput(attrs={
                "placeholder": "PDF ou JPG"
            }),
            "identity_document": forms.ClearableFileInput(attrs={
                "placeholder": "PDF ou JPG"
            }),
            "proof_of_address": forms.ClearableFileInput(attrs={
                "placeholder": "PDF ou JPG"
            }),
        }


    # VALIDATION PERMIS
    def clean_driver_license(self):
        return self.validate_file(
            self.cleaned_data.get("driver_license"),
            required=True,
            field_name="permis de conduire"
        )

    # VALIDATION PIÈCE IDENTITÉ
    def clean_identity_document(self):
        return self.validate_file(
            self.cleaned_data.get("identity_document"),
            required=False,
            field_name="pièce d'identité"
        )

    # VALIDATION JUSTIFICATIF DOMICILE
    def clean_proof_of_address(self):
        return self.validate_file(
            self.cleaned_data.get("proof_of_address"),
            required=False,
            field_name="justificatif de domicile"
        )

    # MÉTHODE GÉNÉRIQUE
    def validate_file(self, file, required, field_name):

        if required and not file:
            raise forms.ValidationError(
                f"Le {field_name} est obligatoire."
            )

        if not file:
            return file

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

    # SAUVEGARDE JSON
    def save(self, commit=True):
        reservation = super().save(commit=False)

        # Convertir la liste en JSON
        reservation.rental_options = self.cleaned_data.get("rental_options", [])

        if commit:
            reservation.save()

        return reservation


class ClientUpdateForm(forms.ModelForm):

    first_name = forms.CharField(
        label="Prénom",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Votre prénom"
        })
    )

    last_name = forms.CharField(
        label="Nom",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Votre nom"
        })
    )

    email = forms.EmailField(
        label="Adresse e-mail",
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "exemple@mail.com"
        })
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

class OptionalPasswordChangeForm(forms.Form):

    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )

    new_password2 = forms.CharField(
        label="Confirmer le mot de passe",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 or password2:

            if password1 != password2:
                raise ValidationError("Les mots de passe ne correspondent pas.")

            validate_password(password1)

        return cleaned_data


