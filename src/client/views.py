from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def client_dashboard(request):
    if request.user.profile.role != 'client':
        raise PermissionDenied

    return render(request, 'client/pageclient.html')

