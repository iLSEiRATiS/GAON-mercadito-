# products/management/commands/seed_products.py
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction

from products.models import Category, Product

CATEGORIAS = [
    "Remeras",
    "Pantalones",
    "Camperas",
    "Zapatillas",
    "Accesorios",
    "Vestidos",
]

# Palabras base para generar nombres distintos, con repetidos por categoría
ADJETIVOS = ["Clásica", "Premium", "Urban", "Básica", "Slim", "Oversize", "Deportiva", "Casual"]
COLORES   = ["Negra", "Blanca", "Azul", "Roja", "Verde", "Beige", "Gris", "Marrón"]
PIEZAS    = ["Remera", "Pantalón", "Campera", "Zapatilla", "Cinturón", "Bufanda", "Vestido", "Short"]

DESCRIPCION_BASE = (
    "Producto de excelente calidad, pensado para uso diario. "
    "Tela suave y resistente. Ideal para combinar y destacar tu estilo."
)

def precio_random():
    # precios verosímiles en ARS
    return Decimal(random.randrange(8_000, 120_000))  # 8k a 120k

def stock_random():
    return random.randint(0, 60)

def pick_image_url(seed: str) -> str:
    """
    Deja una imagen remota genérica (NO fakestore). 
    picsum.photos genera imágenes reproducibles por seed.
    """
    s = slugify(seed) or "gaon"
    # 600x600 cuadrada para cards
    return f"https://picsum.photos/seed/{s}/600/600"

class Command(BaseCommand):
    help = (
        "Genera categorías y N productos aleatorios, borrando previamente los existentes si se indica.\n"
        "Uso: python manage.py seed_products [--clear] [--count 24]"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Borra TODOS los productos existentes antes de sembrar.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=24,
            help="Cantidad total de productos a crear (default 24).",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        clear = opts["clear"]
        count = int(opts["count"] or 24)

        if clear:
            n = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"🧹 Productos eliminados: {n}"))

        # Asegurar categorías locales
        cat_objs = []
        for nombre in CATEGORIAS:
            slug = slugify(nombre)
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={"nombre": nombre})
            # Si el nombre cambió, actualizamos (por si el modelo lo soporta)
            if cat.nombre != nombre:
                cat.nombre = nombre
                cat.save(update_fields=["nombre"])
            cat_objs.append(cat)

        self.stdout.write(self.style.SUCCESS(f"📁 Categorías listas: {', '.join(c.nombre for c in cat_objs)}"))

        creados = 0
        # Garantizamos que haya múltiples productos por categoría (útil para comparar)
        base_por_cat = max(2, count // max(1, len(cat_objs)))  # al menos 2 por categoría
        pool = []

        for cat in cat_objs:
            for _ in range(base_por_cat):
                pool.append(cat)

        # Si faltan para llegar a 'count', completamos al azar
        while len(pool) < count:
            pool.append(random.choice(cat_objs))
        # Si sobran, recortamos
        pool = pool[:count]

        for idx, categoria in enumerate(pool, start=1):
            # Armamos un nombre verosímil
            pieza = random.choice(PIEZAS)
            adj = random.choice(ADJETIVOS)
            color = random.choice(COLORES)
            nombre = f"{pieza} {adj} {color}"

            # Para evitar muchos duplicados exactos, agregamos un nro a veces
            if random.random() < 0.35:
                nombre += f" #{random.randint(1, 99)}"

            precio = precio_random()
            stock  = stock_random()
            desc   = DESCRIPCION_BASE
            image_url = pick_image_url(f"{categoria.slug}-{nombre}")

            p = Product(
                user=None,                 # opcional/nullable en tu modelo
                category=categoria,
                nombre=nombre,
                precio=precio,
                descripcion=desc,
                stock=stock,
                image_url=image_url,       # usamos URL remota genérica (no fakestore)
                activo=True,
            )
            p.save()
            creados += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Seed listo. Productos creados: {creados}"))
