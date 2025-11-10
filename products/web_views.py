# products/web_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Product
from .forms import ProductForm


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
def product_list(request):
    """
    Listado de productos con filtros. Intenta usar 'products/_card.html'
    y si no existe, cae a 'products/list.html' (evita 500 por template faltante).
    """
    q = (request.GET.get("q") or "").strip()
    min_price_raw = (request.GET.get("min_price") or "").strip()
    max_price_raw = (request.GET.get("max_price") or "").strip()
    in_stock = (request.GET.get("in_stock") or "").strip().lower()
    order = (request.GET.get("order") or "").strip().lower()

    min_price = _safe_float(min_price_raw) if min_price_raw else None
    max_price = _safe_float(max_price_raw) if max_price_raw else None

    # ❗ Quitamos `.only(...)` para no depender de que exista image_url u otros campos
    qs = Product.objects.filter(activo=True).select_related("-creado_en")

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))

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
        "in_stock": in_stock,
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

def product_detail(request, pk: int):
    p = get_object_or_404(Product.objects.select_related("-creado_en"), pk=pk, activo=True)
    return render(request, "products/detail.html", {"p": p})


# CREAR PRODUCTO (HTML) – requiere login
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/manage_form.html"
    success_url = reverse_lazy("product-manage")

    def form_valid(self, form):
        # Asignar automáticamente el usuario dueño del producto
        form.instance.user = self.request.user
        messages.success(self.request, "✅ Producto creado con éxito.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        ctx["product"] = None
        return ctx


# GESTIÓN DE PRODUCTOS (owner o staff)
class ProductManageListView(ListView):
    """
    Lista de productos para gestión general (/products/manage/).
    - Si es staff/superuser → ve todos
    - Si NO → se redirige a la vista "mis productos"
    """
    model = Product
    template_name = "products/manage_list.html"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not _is_staff(request.user):
            return redirect("products-mine")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.all().order_by("-creado_en")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "all"
        return ctx


class MyProductsListView(ListView):
    """
    Lista de productos propios (/products/manage/mine/).
    """
    model = Product
    template_name = "products/manage_list.html"
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).order_by("-creado_en")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "mine"
        return ctx

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/manage_form.html"
    success_url = reverse_lazy("product-manage")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        if not (user.is_superuser or user.is_staff or self.object.user_id == user.id):
            messages.error(request, "No tenés permiso para editar este producto.")
            return redirect("product-manage")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.info(self.request, "✏️ Producto actualizado correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = True
        ctx["product"] = self.object
        return ctx

class ProductDeleteView(DeleteView):
    model = Product
    template_name = "products/manage_confirm_delete.html"
    success_url = reverse_lazy("product-manage")
    context_object_name = "obj"  # así matchea con tu template

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = request.user

        if not (_is_staff(user) or self.object.user_id == user.id):
            return HttpResponseForbidden("No sos dueño de este producto.")

        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        _toast(request, "🗑️ Producto eliminado.")
        return super().delete(request, *args, **kwargs)

