import os
from decimal import Decimal
from io import BytesIO
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from PIL import Image, ImageDraw, ImageFont
from products.models import Product, Category

DATA = [
    {"nombre": "Remera GAON", "descripcion": "Remera premium 100% algodón", "precio": "5999.90", "stock": 25, "categoria": "Indumentaria"},
    {"nombre": "Buzo GAON", "descripcion": "Buzo frisa suave", "precio": "18999.00", "stock": 12, "categoria": "Indumentaria"},
    {"nombre": "Zapatillas GAON", "descripcion": "Running livianas", "precio": "25999.00", "stock": 18, "categoria": "Calzado"},
    {"nombre": "Gorra GAON", "descripcion": "Gorra bordada", "precio": "8999.00", "stock": 50, "categoria": "Accesorios"},
    {"nombre": "Mochila GAON", "descripcion": "Mochila urbana 20L", "precio": "21999.00", "stock": 15, "categoria": "Accesorios"},
]

def ensure_category(name: str):
    slug = slugify(name)
    c, _ = Category.objects.get_or_create(nombre=name, defaults={"slug": slug})
    return c

def make_image(label: str, filename: str) -> ContentFile:
    w, h = 800, 600
    img = Image.new("RGB", (w, h), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, (h - th) / 2), label, fill=(20, 20, 20), font=font)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)
    return ContentFile(buf.read(), name=filename)

def pick_owner():
    User = get_user_model()
    for uname in ("admin1", "admin"):
        try:
            return User.objects.get(username=uname)
        except User.DoesNotExist:
            pass
    u = User.objects.filter(is_staff=True).first()
    if u:
        return u
    u = User.objects.first()
    if u:
        return u
    return User.objects.create_superuser("admin1", "admin1@test.com", "admin12345")

class Command(BaseCommand):
    help = "Carga categorías y productos demo con imágenes dummy y asigna un dueño al producto"

    def handle(self, *args, **opts):
        owner = pick_owner()
        product_fields = {f.name for f in Product._meta.get_fields() if getattr(f, "concrete", False)}
        owner_field = next((n for n in ("user", "owner", "created_by") if n in product_fields), None)
        created = 0

        for row in DATA:
            cat = ensure_category(row["categoria"])

            defaults = {}
            if "descripcion" in product_fields: defaults["descripcion"] = row["descripcion"]
            if "precio" in product_fields: defaults["precio"] = Decimal(row["precio"])
            if "stock" in product_fields: defaults["stock"] = int(row["stock"])
            if "activo" in product_fields: defaults["activo"] = True
            if "category" in product_fields: defaults["category"] = cat
            if owner_field: defaults[owner_field] = owner

            p, was_created = Product.objects.get_or_create(
                nombre=row["nombre"],
                defaults=defaults
            )

            if was_created:
                created += 1
                if "imagen" in product_fields:
                    filename = f"{slugify(row['nombre'])}.jpg"
                    content = make_image(row["nombre"], filename)
                    try:
                        p.imagen.save(filename, content, save=True)
                    except Exception:
                        pass

        msg = f"Semilla completada. Productos creados: {created}"
        if owner_field:
            msg += f" | Propietario: {owner} via campo '{owner_field}'"
        self.stdout.write(self.style.SUCCESS(msg))
