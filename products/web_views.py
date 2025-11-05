from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Product, Category
from .forms import ProductForm, CategoryForm


# --- helpers ---
def _toast(request, txt):
    messages.success(request, txt)

def _is_staff(user):
    return user.is_staff or user.is_superuser


# -------------------------------
# TIENDA PÚBLICA
# -------------------------------
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


# -----------------------------------
# CREAR PRODUCTO (HTML) – requiere login
# Reutiliza manage_form.html
# -----------------------------------
@login_required
@ensure_csrf_cookie
@csrf_protect
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.user = request.user
            prod.save()
            _toast(request, "Producto creado")
            return redirect('product-manage')
    else:
        form = ProductForm()
    return render(request, 'products/manage_form.html', {'form': form, 'is_edit': False, 'product': None})


# -----------------------------------
# GESTIÓN DE CATEGORÍAS (solo staff/admin)
# -----------------------------------
@login_required
def category_list(request):
    if not _is_staff(request.user):
        return HttpResponseForbidden("Solo staff.")
    qs = Category.objects.order_by("nombre")
    return render(request, "categories/manage/list.html", {"items": qs})

@login_required
@csrf_protect
def category_create(request):
    if not _is_staff(request.user):
        return HttpResponseForbidden("Solo staff.")
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        _toast(request, "Categoría creada")
        return redirect("/categories/manage/")
    return render(request, "categories/manage/form.html", {"form": form, "mode": "create"})

@login_required
@csrf_protect
def category_update(request, pk):
    if not _is_staff(request.user):
        return HttpResponseForbidden("Solo staff.")
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        _toast(request, "Categoría actualizada")
        return redirect("/categories/manage/")
    return render(request, "categories/manage/form.html", {"form": form, "mode": "edit", "obj": obj})

@login_required
@csrf_protect
def category_delete(request, pk):
    if not _is_staff(request.user):
        return HttpResponseForbidden("Solo staff.")
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        _toast(request, "Categoría eliminada")
        return redirect("/categories/manage/")
    return render(request, "categories/manage/confirm_delete.html", {"obj": obj})


# -----------------------------------
# GESTIÓN DE PRODUCTOS (owner o staff)
# -----------------------------------
@login_required
def my_products(request):
    qs = Product.objects.all().order_by("-creado_en")
    if not _is_staff(request.user):
        qs = qs.filter(user=request.user)

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "products/manage_list.html", {"page_obj": page_obj})

@login_required
@ensure_csrf_cookie
@csrf_protect
def product_manage_edit(request, pk):
    prod = get_object_or_404(Product, pk=pk)
    if not (request.user.is_superuser or request.user.is_staff or prod.user_id == request.user.id):
        messages.error(request, "No tenés permiso para editar este producto.")
        return redirect('product-manage')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect('product-manage')
    else:
        form = ProductForm(instance=prod)

    return render(request, 'products/manage_form.html', {'form': form, 'is_edit': True, 'product': prod})

@login_required
@ensure_csrf_cookie
@csrf_protect
def product_delete(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if not _is_staff(request.user) and obj.user_id != request.user.id:
        return HttpResponseForbidden("No sos dueño de este producto.")

    if request.method == "POST":
        obj.delete()
        _toast(request, "Producto eliminado")
        return redirect("product-manage")

    return render(request, "products/manage_confirm_delete.html", {"product": obj})

@login_required
def product_manage(request):
    """
    Gestión completa de productos (solo staff/admin).
    Si NO sos staff, redirige a 'mis productos'.
    Renderiza templates/products/manage_list.html
    """
    if not _is_staff(request.user):
        return redirect("products-mine")

    qs = Product.objects.all().order_by("-creado_en")
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(
        request,
        "products/manage_list.html",
        {"page_obj": page_obj, "mode": "all"},
    )


@login_required
def product_manage_mine(request):
    """
    Gestión de MIS productos (dueño logueado).
    Renderiza templates/products/manage_list.html
    """
    qs = Product.objects.filter(user=request.user).order_by("-creado_en")
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(
        request,
        "products/manage_list.html",
        {"page_obj": page_obj, "mode": "mine"},
    )