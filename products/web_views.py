from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Product, Category
from .forms import ProductForm

@ensure_csrf_cookie
def product_list(request):
    qs = Product.objects.filter(activo=True)
    q = request.GET.get('q') or ''
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    min_price = request.GET.get('min_price') or ''
    max_price = request.GET.get('max_price') or ''
    if min_price:
        qs = qs.filter(precio__gte=min_price)
    if max_price:
        qs = qs.filter(precio__lte=max_price)
    cat = request.GET.get('category') or ''
    if cat:
        qs = qs.filter(category__slug=cat)
    in_stock = (request.GET.get('in_stock') or '').lower()
    if in_stock == 'true':
        qs = qs.filter(stock__gt=0)
    elif in_stock == 'false':
        qs = qs.filter(stock__lte=0)
    order = (request.GET.get('order') or '').lower()
    if order == 'price_asc':
        qs = qs.order_by('precio', '-creado_en')
    elif order == 'price_desc':
        qs = qs.order_by('-precio', '-creado_en')
    elif order == 'name':
        qs = qs.order_by('nombre', '-creado_en')
    elif order == 'oldest':
        qs = qs.order_by('creado_en')
    else:
        qs = qs.order_by('-creado_en')
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    ctx = {
        'page_obj': page_obj,
        'q': q,
        'min_price': min_price,
        'max_price': max_price,
        'order': order,
        'category': cat,
        'in_stock': in_stock,
        'categories': Category.objects.order_by('nombre'),
    }
    return render(request, 'products/list.html', ctx)

@ensure_csrf_cookie
def product_detail(request, pk):
    p = get_object_or_404(Product, pk=pk, activo=True)
    return render(request, 'products/detail.html', {'p': p})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.user = request.user
            prod.save()
            return redirect('products-list')
    else:
        form = ProductForm()
    return render(request, 'products/create.html', {'form': form})
