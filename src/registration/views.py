from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ClientRegisterForm
from accounts.models import Profile

def register_view(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()


            Profile.objects.create(
                user=user,
                role='client'
            )

            messages.success(request, "Compte client créé avec succès !")
            return redirect('login')
    else:
        form = ClientRegisterForm()

    return render(request, 'registration/register.html', {'form': form})
