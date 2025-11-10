from django.conf import settings
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)[:70]
        super().save(*args, **kwargs)


class Post(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    categoria = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="posts")

    slug = models.SlugField(max_length=220, unique=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_pinned", "creado_en"]),
            models.Index(fields=["slug"]),
        ]
        ordering = ["-is_pinned", "-creado_en"]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)[:200] or "post"
            s = base
            n = 1
            while Post.objects.filter(slug=s).exclude(pk=self.pk).exists():
                n += 1
                s = f"{base}-{n}"
            self.slug = s
        super().save(*args, **kwargs)


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comentarios")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comentarios")
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Comentario de {self.autor} en {self.post}"
