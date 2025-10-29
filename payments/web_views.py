from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def mp_success(request):
    return render(request, 'payments/success.html')

@ensure_csrf_cookie
def mp_failure(request):
    return render(request, 'payments/failure.html')

@ensure_csrf_cookie
def mp_pending(request):
    return render(request, 'payments/pending.html')
