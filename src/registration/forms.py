from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class ClientRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, label="Prénom")
    last_name = forms.CharField(max_length=100, label="Nom")
    email = forms.EmailField(label="Adresse email")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà utilisé.")

        return username