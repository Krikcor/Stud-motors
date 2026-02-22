from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from accounts.models import Profile
from .forms import ClientRegisterForm

# IMPORTS
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings


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

                # 👇 AJOUT : génération lien activation
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                activation_link = request.build_absolute_uri(
                    reverse("activate_account", kwargs={
                        "uidb64": uid,
                        "token": token
                    })
                )

                send_mail(
                    subject="Activation de votre compte",
                    message=f"Bonjour,\n\nCliquez ici pour activer votre compte :\n{activation_link}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
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


# Activation
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        messages.success(request, "Votre compte est activé.")
        return redirect('login')
    else:
        return render(request, 'registration/activation_invalid.html')