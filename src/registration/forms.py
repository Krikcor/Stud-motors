from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ClientRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, label="Prénom")
    last_name = forms.CharField(max_length=100, label="Nom")
    email = forms.EmailField(label="Adresse email")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']
