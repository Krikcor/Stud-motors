from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import Profile
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    if request.user.is_authenticated:
        if request.user.profile.role == 'pro':
            return redirect('pro_dashboard')
        else:
            return redirect('client_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            logger.info(f"Connexion réussie: {username}")
            try:
                profile = user.profile
                if profile.role == 'pro':
                    return redirect('pro_dashboard')
                elif profile.role == 'client':
                    return redirect('client_dashboard')
            except Profile.DoesNotExist:
                logger.error(f"Profil manquant pour: {username}")
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
                return redirect('login')
        else:
            logger.warning(f"Échec login: {username}")
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")

    return render(request, 'accounts/login.html')
