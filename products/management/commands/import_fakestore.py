import sys
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from products.models import Product, Category


FAKESTORE_URL = "https://fakestoreapi.com/products/category/{}"
CLOTHING_CATS = [
    "men's clothing",
    "women's clothing",
]


def _safe_print(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def download_image(url: str, timeout=12) -> bytes | None:
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200 and r.content:
            return r.content
    except Exception:
        return None
    return None


def has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


def list_fields(model):
    return [f.name for f in model._meta.get_fields() if hasattr(f, "name")]


def _detect_category_fields():
    """
    Detecta el campo "nombre" y el campo "slug" (si existe) de Category.
    name_field puede ser: name / title / nombre / label
    slug_field por lo general: slug (si no existe, devolvemos None)
    """
    candidates_name = ["name", "title", "nombre", "label"]
    name_field = next((f for f in candidates_name if has_field(Category, f)), None)

    slug_field = "slug" if has_field(Category, "slug") else None
    return name_field, slug_field


def ensure_category(name_value: str) -> Category:
    """
    Crea/obtiene Category usando los campos detectados.
    Si no hay slug, matchea por nombre (case-insensitive).
    """
    name_field, slug_field = _detect_category_fields()
    if not name_field and not slug_field:
        raise CommandError(
            "No pude detectar campos de texto en Category (ninguno de: name/title/nombre/label ni slug)."
        )

    # Filtros + defaults
    slug_value = slugify(name_value)
    if slug_field:
        filters = {slug_field: slug_value}
    else:
        # Sin slug: usamos nombre icontains/iexact => get_or_create requiere igualdad exacta.
        # Probamos primero exacto, si no existe, creamos.
        filters = {name_field: name_value}

    defaults = {}
    if name_field:
        defaults[name_field] = name_value
    if slug_field:
        defaults[slug_field] = slug_value

    try:
        cat, created = Category.objects.get_or_create(**filters, defaults=defaults)
    except Exception as e:
        raise CommandError(f"Error al crear/obtener Category con filters={filters}, defaults={defaults}: {e}")

    # Si se creó y el nombre no coincide (o luego querés normalizar), lo actualizamos
    if name_field and getattr(cat, name_field, None) != name_value:
        setattr(cat, name_field, name_value)
        cat.save(update_fields=[name_field])

    return cat


class Command(BaseCommand):
    help = (
        "Importa productos de FakeStore (solo ropa), con conversión USD→ARS.\n"
        "Uso: python manage.py import_fakestore [--clear] [--limit 40] [--download-images] [--fx 1500]"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Borra TODOS los productos existentes antes de importar.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Límite total de productos a importar (0 = sin límite).",
        )
        parser.add_argument(
            "--download-images",
            action="store_true",
            help="Descarga las imágenes a MEDIA (requiere que Product.image sea ImageField).",
        )
        parser.add_argument(
            "--fx",
            type=float,
            default=1500.0,
            help="Multiplicador de conversión USD→ARS (por defecto 1500).",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        clear = opts["clear"]
        limit = int(opts["limit"] or 0)
        download_images = opts["download_images"]
        fx = float(opts["fx"] or 1500.0)

        # Debug útil de campos reales en tus modelos
        _safe_print(f"Category fields: {', '.join(list_fields(Category))}")
        _safe_print(f"Product  fields: {', '.join(list_fields(Product))}")

        # Detectar campos del modelo Product
        name_field = next((f for f in ["name", "title", "nombre"] if has_field(Product, f)), None)
        price_field = next((f for f in ["price", "precio"] if has_field(Product, f)), None)
        desc_field = next((f for f in ["description", "descripcion", "detalle"] if has_field(Product, f)), None)
        image_field = next((f for f in ["image", "imagen"] if has_field(Product, f)), None)
        image_url_field = "image_url" if has_field(Product, "image_url") else None
        category_fk_field = "category" if has_field(Product, "category") else None
        stock_field = "stock" if has_field(Product, "stock") else None
        currency_field = next((f for f in ["currency", "moneda"] if has_field(Product, f)), None)

        if not name_field or not price_field:
            raise CommandError(
                "No encuentro campos obligatorios en Product. Necesito al menos name/nombre y price/precio."
            )

        if download_images and not image_field:
            _safe_print("⚠️  --download-images activado pero Product.image no existe. Se ignorará la descarga.")

        if not image_field and not image_url_field:
            _safe_print("ℹ️  No hay ni image(ImageField) ni image_url(CharField). Se importará sin imagen.")

        if clear:
            cnt = Product.objects.all().count()
            Product.objects.all().delete()
            _safe_print(f"🧹 Productos eliminados: {cnt}")

        _safe_print(f"💱 Conversión: 1 USD → {fx:.2f} ARS")
        total_importados = 0
        errores = 0

        for cat_api in CLOTHING_CATS:
            url = FAKESTORE_URL.format(requests.utils.quote(cat_api, safe=""))
            _safe_print(f"↓ Descargando: {url}")
            try:
                res = requests.get(url, timeout=20)
                res.raise_for_status()
                items = res.json()
                if not isinstance(items, list):
                    _safe_print(f"⚠️ Respuesta inesperada para {cat_api}: {items!r}")
                    continue
            except Exception as e:
                _safe_print(f"❌ Error obteniendo {cat_api}: {e}")
                errores += 1
                continue

            # Asegurar categoría local (Hombre/Mujer) con los campos que existan
            nombre_cat_local = "Hombre" if "men" in cat_api else "Mujer"
            cat_obj = ensure_category(nombre_cat_local) if category_fk_field else None

            for it in items:
                if limit and total_importados >= limit:
                    break

                try:
                    title = (it.get("title") or "").strip()
                    desc = (it.get("description") or "").strip()
                    price_usd = float(it.get("price") or 0.0)
                    price_ars = round(price_usd * fx, 2)

                    prod = Product()
                    setattr(prod, name_field, title)
                    setattr(prod, price_field, price_ars)
                    if desc_field:
                        setattr(prod, desc_field, desc)
                    if category_fk_field and cat_obj:
                        setattr(prod, category_fk_field, cat_obj)
                    if stock_field:
                        setattr(prod, stock_field, 25)
                    if currency_field:
                        setattr(prod, currency_field, "ARS")

                    prod.save()  # para obtener PK

                    # Imagen
                    source_img = it.get("image") or ""
                    if source_img:
                        if download_images and image_field:
                            content = download_image(source_img)
                            if content:
                                parsed = urlparse(source_img)
                                base = parsed.path.rsplit("/", 1)[-1] or "image.jpg"
                                filename = f"fk_{prod.pk}_{base}"
                                getattr(prod, image_field).save(filename, ContentFile(content), save=True)
                            elif image_url_field:
                                setattr(prod, image_url_field, source_img)
                                prod.save(update_fields=[image_url_field])
                        elif image_url_field:
                            setattr(prod, image_url_field, source_img)
                            prod.save(update_fields=[image_url_field])

                    total_importados += 1

                except Exception as e:
                    errores += 1
                    _safe_print(f"   • Error con item '{it.get('title','(sin título)')[:40]}': {e}")

                if limit and total_importados >= limit:
                    break

            if limit and total_importados >= limit:
                break

        _safe_print(f"✅ Importación terminada. Importados: {total_importados} • Errores: {errores}")
