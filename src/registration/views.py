from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from accounts.models import Profile
from .forms import ClientRegisterForm


def register_view(request):

    # Empêche un utilisateur déjà connecté de se réinscrire
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Création de l'utilisateur
                    user = form.save()

                    # Création du profil
                    Profile.objects.create(
                        user=user,
                        role='client'
                    )

                # Connexion automatique après inscription
                login(request, user)

                messages.success(request, "Compte client créé avec succès !")
                return redirect('client_dashboard')

            except Exception:
                messages.error(request, "Une erreur est survenue. Veuillez réessayer.")
    else:
        form = ClientRegisterForm()

    return render(request, 'registration/register.html', {'form': form})