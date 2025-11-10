# GAON - Mercadito

Proyecto Django para un marketplace educativo con funciones: catálogo de productos, carrito, pagos, foro y asistente (chat) integrado.

Este README explica cómo poner el proyecto en marcha en desarrollo, cómo funcionan las subidas de imágenes (MEDIA), y notas importantes sobre autenticación token ↔ sesión y CSRF.

## Contenido
- [Requisitos](#requisitos)
- [Estructura principal](#estructura-principal)
- [Instalación rápida (dev)](#instalación-rápida-dev)
- [Variables de entorno (.env)](#variables-de-entorno-env)
- [Migraciones y base de datos](#migraciones-y-base-de-datos)
- [Archivos media (imágenes)](#archivos-media-imágenes)
- [Endpoints y rutas útiles](#endpoints-y-rutas-útiles)
- [Autenticación y CSRF (nota importante)](#autenticación-y-csrf-nota-importante)
- [Pruebas](#pruebas)
- [Problemas comunes y soluciones](#problemas-comunes-y-soluciones)
- [Cómo contribuir](#cómo-contribuir)

---

## Requisitos
- Python 3.10+
- Virtualenv / venv
- pip

El proyecto usa las dependencias en `requirements.txt` (incluye `Django`, `djangorestframework`, `pillow`, `django-environ`, etc.).

## Estructura principal (resumen)
- `gaon/` - configuración del proyecto (settings, urls, asgi/wsgi)
- `products/` - modelo `Product` con `ImageField` y formularios/web_views para crear/editar productos
- `chat/` - API y lógica del asistente (chat)
- `foro/` - app del foro (posts y comentarios; API + web views)
- `templates/` - templates globales: `base.html`, `home.html`, etc.
- `static/` - recursos estáticos de desarrollo
- `media/` - donde se guardan las imágenes subidas (configurado por `MEDIA_ROOT`)

## Instalación rápida (dev)
1. Clonar repo
```powershell
git clone <repo-url> .
```

2. Crear virtualenv e instalar dependencias
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
pip install --upgrade pip
pip install -r requirements.txt
```

3. Variables de entorno
- Crea un archivo `.env` en la raíz o exporta variables. Ver sección siguiente.

4. Migraciones y crear superuser
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Levantar servidor en modo desarrollo
```powershell
python manage.py runserver
```

6. Abrir en el navegador: http://127.0.0.1:8000/

## Variables de entorno (.env)
Se usa `django-environ` para leer `.env`. Variables relevantes (ejemplos):

```
SECRET_KEY=dev-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
SITE_URL=
GEMINI_API_KEY=    # opcional, para asistente si usás Gemini
MP_ACCESS_TOKEN=   # MercadoPago
MP_PUBLIC_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Ajustá según sea necesario.

## Migraciones y base de datos
- En desarrollo usamos SQLite por defecto (`db.sqlite3`).
- Si añades/editas modelos, ejecuta `makemigrations` y `migrate`.

```powershell
python manage.py makemigrations
python manage.py migrate
```

Nota: si `makemigrations` falla por `ModuleNotFoundError: No module named 'environ'`, instalá las dependencias (`pip install -r requirements.txt`).

## Archivos media (imágenes)
- `MEDIA_ROOT` está configurado en `gaon/settings.py`:
  - `MEDIA_URL = '/media/'`
  - `MEDIA_ROOT = BASE_DIR / 'media'`
- En desarrollo, `gaon/urls.py` añade `+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` para servir `media/` automáticamente.

Subida de imágenes para productos
- El modelo `products.Product` define `imagen = models.ImageField(upload_to=product_upload_to, blank=True, null=True)`.
- El formulario `products/forms.py` incluye ese campo, y `templates/products/manage_form.html` ya tiene `enctype="multipart/form-data"` para permitir la subida desde la web.
- Las imágenes se guardan en `media/products/<uuid>.<ext>`.

Verificá permisos y existencia de la carpeta `media/` si la subida falla.

## Endpoints y rutas útiles
- Web
  - `/` -> home
  - `/products/` -> listado público
  - `/products/<id>/` -> detalle producto
  - `/products/manage/new/` -> crear producto (requiere autenticación)
  - `/products/manage/` -> gestión (staff) o `/products/manage/mine/` -> mis productos
  - `/account/` -> panel usuario
- API
  - `/api/chat/` (GET lista, POST crear mensaje del usuario)
  - `/api/chat/welcome/` (POST) -> crea mensaje de bienvenida del asistente para el usuario
  - `/api/foro/...` -> endpoints del foro (comentarios, posts)
  - `/api/products/` -> API de productos (si está expuesto)

Consulta el router de cada app para más rutas.

## Autenticación y CSRF (nota importante)
- El proyecto soporta **Token Authentication** (DRF) y **SessionAuthentication** (Django sessions).
- Flujo usado en frontend: muchos clientes guardan un token en `localStorage` y la página cliente convierte ese token en *cookie de sesión* (`/api/auth/session/`) para poder usar vistas CSRF-protegidas: la cookie y CSRF deben coincidir.
- En `templates/base.html` hay utilidades JS expuestas: `window.GAON_AUTH` con `hasToken()`, `authHeader()` y `ensureDjangoSessionFromToken()`.
- Problemas comunes:
  - CSRF 403 al enviar un formulario después de autenticar con token: suele suceder si la cookie de sesión (y por tanto el csrftoken) se actualizó después de que la página renderizó el input oculto con un csrf antiguo. Solución: sincronizar el input csrf con la cookie antes del submit (ya añadido en `manage_form.html`) o recargar tras crear la sesión.

## Pruebas
- Ejecutar tests Django:
```powershell
python manage.py test
```
- Agregar tests específicos: se recomienda añadir tests para `/api/chat/`, `/api/foro/` y los formularios de subida de imágenes.

## Problemas comunes y soluciones rápidas
- Error `ModuleNotFoundError: No module named 'environ'` al ejecutar `manage.py`: instalar dependencias (`pip install -r requirements.txt`).
- Imágenes no cargan en `/media/`: comprobar `MEDIA_ROOT` y que `DEBUG=True` para desarrollo; revisá `gaon/urls.py` tiene `static(...)` (ya incluido).
- CSRF 403 tras logueo por token: usar `ensureDjangoSessionFromToken()` o sincronizar token CSRF antes de submit.

## Despliegue (Docker / Render / PythonAnywhere)

Dockerfile
- Hay un `Dockerfile` en la raíz preparado para una imagen básica que ejecuta Gunicorn. Pasos sugeridos:

  1. Construir la imagen localmente:
  ```powershell
  docker build -t gaon-mercadito .
  ```

  2. Ejecutar contenedor (exponiendo puerto 8000):
  ```powershell
  docker run -e SECRET_KEY="mi-secret" -e DEBUG=False -p 8000:8000 gaon-mercadito
  ```

Render
- Render acepta repositorios con Dockerfile. Crear un servicio web con "Docker" como tipo de build y exponer puerto 8000.
- Variables de entorno importantes: `SECRET_KEY`, `DEBUG=False`, `MP_ACCESS_TOKEN`, `GEMINI_API_KEY` (si usás asistente), `SITE_URL`.

PythonAnywhere
- PythonAnywhere no usa Docker; en vez de eso:
  - Crear un virtualenv, subir código, instalar `requirements.txt`.
  - Configurar WSGI para apuntar a `gaon.wsgi:application`.
  - En `Settings > Web` configurar static/media y ruta a `media/`.

Notas de seguridad
- Nunca expongas `SECRET_KEY` ni claves en repositorios públicos. Usá las variables de entorno del proveedor.
- Para producción, configurá `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, `DEBUG=False`, y served media desde un bucket/ CDN.