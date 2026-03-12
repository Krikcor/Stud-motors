from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import Profile
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Retourne l'IP réelle du client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def login_view(request):
    ip = get_client_ip(request)
    logger.info(f"Tentative d'accès à la page de login depuis l'IP {ip}")

    cache_key = f'login_attempts_{ip}'
    attempts_data = cache.get(cache_key, {'count': 0, 'blocked_until': None})
    now = timezone.now()
    blocked_until = attempts_data.get('blocked_until')

    # Vérifie si l'IP est bloquée
    if blocked_until and now < blocked_until:
        remaining = int((blocked_until - now).total_seconds() / 60) + 1
        logger.warning(f"Tentative de connexion depuis une IP bloquée : {ip}")
        messages.error(request, f"Trop de tentatives. Réessayez dans {remaining} minute(s).")
        return render(request, 'accounts/login.html')

    # Si utilisateur déjà connecté
    if request.user.is_authenticated:
        logger.info(f"Utilisateur déjà connecté : {request.user.username}")
        try:
            role = request.user.profile.role
            if role == 'pro':
                return redirect('pro_dashboard')
            elif role == 'client':
                return redirect('client_dashboard')
        except Profile.DoesNotExist:
            logger.error(f"Profil utilisateur manquant pour {request.user.username}")
            messages.error(request, "Profil utilisateur manquant")
            return render(request, 'accounts/login.html')

    # POST => tentative de login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        logger.info(f"Tentative de connexion pour l'utilisateur : {username}")

        user = authenticate(request, username=username, password=password)

        if user:
            logger.info(f"Connexion réussie pour l'utilisateur : {username}")
            login(request, user)

            # Supprime le compteur si login réussi
            cache.delete(cache_key)

            try:
                role = user.profile.role
                if role == 'pro':
                    return redirect('pro_dashboard')
                elif role == 'client':
                    return redirect('client_dashboard')
            except Profile.DoesNotExist:
                logger.error(f"Profil manquant pour: {username}")
                messages.error(request, "Profil utilisateur manquant")
                return render(request, 'accounts/login.html')
        else:
            # Login échoué => incrémente compteur
            attempts = attempts_data.get('count', 0) + 1

            if attempts >= 5:
                blocked_until = now + timedelta(minutes=30)
                cache.set(cache_key, {'count': attempts, 'blocked_until': blocked_until}, 1800)
                logger.warning(f"IP {ip} bloquée après {attempts} tentatives")
                messages.error(request, "Trop de tentatives. Réessayez dans 30 minutes.")
            else:
                cache.set(cache_key, {'count': attempts, 'blocked_until': None}, 3600)
                logger.warning(f"Échec login: {username} (tentative {attempts})")
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")

            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')