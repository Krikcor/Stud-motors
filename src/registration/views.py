from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ClientRegisterForm

def register_view(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Compte créé avec succès !")
            return redirect('login')
    else:
        form = ClientRegisterForm()

    return render(request, 'registration/register.html', {'form': form})
