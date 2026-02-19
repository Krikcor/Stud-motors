from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import Profile

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                profile = user.profile
                if profile.role == 'pro':
                    return redirect('pro_dashboard')
                elif profile.role == 'client':
                    return redirect('client_dashboard')
            except Profile.DoesNotExist:
                messages.error(request, "Profil non trouvé")
                return redirect('login')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
    return render(request, 'accounts/login.html')
