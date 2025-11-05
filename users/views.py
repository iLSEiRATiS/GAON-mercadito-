from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib import messages
from .forms import ProfileForm

@ensure_csrf_cookie
def login_page(request):
    return render(request, 'users/login.html')

@ensure_csrf_cookie
def signup_page(request):
    return render(request, 'users/signup.html')

@ensure_csrf_cookie
def account_page(request):
    return render(request, 'users/account.html')

@login_required
def social_bridge(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    ctx = {"token": token.key, "redirect_to": "/products/"}
    return render(request, "users/social_bridge.html", ctx)

@require_POST
@csrf_exempt
def session_from_token(request):
    auth = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth.startswith('Token '):
        return HttpResponseForbidden('Missing token')
    key = auth.split(' ', 1)[1].strip()
    try:
        token = Token.objects.get(key=key)
    except Token.DoesNotExist:
        return HttpResponseForbidden('Bad token')
    login(request, token.user)  # => setea cookie de sesión
    return JsonResponse({'ok': True})

@login_required
def account_edit(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos actualizados correctamente.")
            return redirect("/account/")  # o quedate en la misma página si preferís
    else:
        form = ProfileForm(instance=user)
    return render(request, "users/account_edit.html", {"form": form})
