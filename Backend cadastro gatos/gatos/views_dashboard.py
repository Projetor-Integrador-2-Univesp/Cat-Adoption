from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@login_required(login_url='login')
@ensure_csrf_cookie
def dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied("Acesso restrito à administração.")
    return render(request, 'gatos/dashboard.html')
