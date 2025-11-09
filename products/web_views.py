# products/web_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template import TemplateDoesNotExist
from django.template.loader import select_template

from .models import Product, Category
from .forms import ProductForm, CategoryForm


# Helpers
def _toast(request, txt: str) -> None:
    messages.success(request, txt)

def _is_staff(user) -> bool:
    return bool(user.is_staff or user.is_superuser)

def _safe_float(val: str):
    if val is None:
        return None
    s = str(val).strip().replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


# TIENDA PÚBLICA
@ensure_csrf_cookie
def product_list(request):
    """
    Listado de productos con filtros. Intenta usar 'products/_card.html'
    y si no existe, cae a 'products/list.html' (evita 500 por template faltante).
    """
    q = (request.GET.get("q") or "").strip()
    min_price_raw = (request.GET.get("min_price") or "").strip()
    max_price_raw = (request.GET.get("max_price") or "").strip()
    cat_slug = (request.GET.get("category") or "").strip()
    in_stock = (request.GET.get("in_stock") or "").strip().lower()
    order = (request.GET.get("order") or "").strip().lower()

    min_price = _safe_float(min_price_raw) if min_price_raw else None
    max_price = _safe_float(max_price_raw) if max_price_raw else None

    # ❗ Quitamos `.only(...)` para no depender de que exista image_url u otros campos
    qs = Product.objects.filter(activo=True).select_related("category")

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))

    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)

    if min_price is not None:
        qs = qs.filter(precio__gte=min_price)
    if max_price is not None:
        qs = qs.filter(precio__lte=max_price)

    if in_stock == "true":
        qs = qs.filter(stock__gt=0)
    elif in_stock == "false":
        qs = qs.filter(stock__lte=0)

    if order == "oldest":
        qs = qs.order_by("creado_en")
    elif order == "price_asc":
        qs = qs.order_by("precio", "-creado_en")
    elif order == "price_desc":
        qs = qs.order_by("-precio", "-creado_en")
    elif order == "name":
        qs = qs.order_by("nombre", "-creado_en")
    else:
        qs = qs.order_by("-creado_en")

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    ctx = {
        "page_obj": page_obj,
        "q": q,
        "min_price": min_price_raw,
        "max_price": max_price_raw,
        "order": order,
        "category": cat_slug,
        "in_stock": in_stock,
        "categories": Category.objects.order_by("nombre"),
    }

    try:
        tpl = select_template(["products/_card.html", "products/list.html"])
        return render(request, tpl.template.name, ctx)
    except TemplateDoesNotExist as e:
        messages.error(request, f"No se encontró template de productos: {e}")
        return render(request, "base.html", {"content": f"Falta template: {e}", **ctx}, status=500)
    except Exception as e:
        import traceback; traceback.print_exc()
        messages.error(request, f"Error al renderizar productos: {e}")
        return render(request, "base.html", {"content": f"Error: {e}", **ctx}, status=500)


@ensure_csrf_cookie
def product_detail(request, pk: int):
    p = get_object_or_404(Product.objects.select_related("category"), pk=pk, activo=True)
    return render(request, "products/detail.html", {"p": p})


# CREAR PRODUCTO (HTML) – requiere login
@login_required
@ensure_csrf_cookie
@csrf_protect
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.user = request.user
            prod.save()
            _toast(request, "Producto creado")
            return redirect("product-manage")
    else:
        form = ProductForm()
    return render(request, "products/manage_form.html", {"form": form, "is_edit": False, "product": None})


# GESTIÓN DE CATEGORÍAS (solo staff/admin)
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
def category_update(request, pk: int):
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
def category_delete(request, pk: int):
    if not _is_staff(request.user):
        return HttpResponseForbidden("Solo staff.")
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        _toast(request, "Categoría eliminada")
        return redirect("/categories/manage/")
    return render(request, "categories/manage/confirm_delete.html", {"obj": obj})


# GESTIÓN DE PRODUCTOS (owner o staff)
@login_required
def my_products(request):
    qs = Product.objects.all().order_by("-creado_en")
    if not _is_staff(request.user):
        qs = qs.filter(user=request.user)
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "products/manage_list.html", {"page_obj": page_obj})

@login_required
@ensure_csrf_cookie
@csrf_protect
def product_manage_edit(request, pk: int):
    prod = get_object_or_404(Product, pk=pk)
    if not (request.user.is_superuser or request.user.is_staff or prod.user_id == request.user.id):
        messages.error(request, "No tenés permiso para editar este producto.")
        return redirect("product-manage")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect("product-manage")
    else:
        form = ProductForm(instance=prod)

    return render(request, "products/manage_form.html", {"form": form, "is_edit": True, "product": prod})

@login_required
@ensure_csrf_cookie
@csrf_protect
def product_delete(request, pk: int):
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
    if not _is_staff(request.user):
        return redirect("products-mine")
    qs = Product.objects.all().order_by("-creado_en")
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "products/manage_list.html", {"page_obj": page_obj, "mode": "all"})

@login_required
def product_manage_mine(request):
    qs = Product.objects.filter(user=request.user).order_by("-creado_en")
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "products/manage_list.html", {"page_obj": page_obj, "mode": "mine"})
