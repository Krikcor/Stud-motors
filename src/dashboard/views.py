from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

@login_required
def pro_dashboard(request):
    if request.user.profile.role != 'pro':
        raise PermissionDenied

    return render(request, 'dashboard/pro_dashboard.html')

