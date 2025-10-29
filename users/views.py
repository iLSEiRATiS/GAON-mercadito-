from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def login_page(request):
    return render(request, 'users/login.html')

@ensure_csrf_cookie
def signup_page(request):
    return render(request, 'users/signup.html')

@ensure_csrf_cookie
def account_page(request):
    return render(request, 'users/account.html')
