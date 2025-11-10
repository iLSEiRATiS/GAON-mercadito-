from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.core.cache import cache
from django.db.models import Count, Q

from .models import Post, Category
from .forms import ComentarioForm


class ForoListView(ListView):
    template_name = "foro/post_list.html"
    context_object_name = "posts"
    paginate_by = 9

    def get_queryset(self):
        qs = (
            Post.objects
            .filter(is_active=True)
            .select_related("autor", "categoria")
            .annotate(num_comentarios=Count("comentarios"))
        )

        q = self.request.GET.get("q", "").strip()
        cat = self.request.GET.get("cat", "").strip()
        order = self.request.GET.get("order", "new")

        if q:
            qs = qs.filter(Q(titulo__icontains=q) | Q(contenido__icontains=q))

        if cat:
            qs = qs.filter(categoria__slug=cat)

        # pinned siempre primero
        if order == "comments":
            qs = qs.order_by("-is_pinned", "-num_comentarios", "-creado_en")
        else:  # "new"
            qs = qs.order_by("-is_pinned", "-creado_en")

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["order"] = self.request.GET.get("order", "new")
        ctx["cat"] = self.request.GET.get("cat", "")
        ctx["cats"] = Category.objects.all()
        return ctx


@ensure_csrf_cookie
@csrf_protect
def foro_detail(request, pk=None, slug=None):
    # aceptar pk o slug
    if slug:
        post = get_object_or_404(Post, slug=slug, is_active=True)
    else:
        post = get_object_or_404(Post, pk=pk, is_active=True)

    comentarios = post.comentarios.select_related("autor")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        # Rate limit: 1 comentario cada 10 segundos por usuario/post
        rl_key = f"rl:comment:{request.user.id}:{post.id}"
        if cache.get(rl_key):
            form = ComentarioForm()
            return render(
                request,
                "foro/post_detail.html",
                {
                    "post": post,
                    "comentarios": comentarios,
                    "form": form,
                    "rate_limited": True,
                }
            )

        form = ComentarioForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.autor = request.user
            c.post = post
            c.save()
            cache.set(rl_key, True, timeout=10)
            return redirect("foro:detail-slug", slug=post.slug)
    else:
        form = ComentarioForm()

    return render(
        request,
        "foro/post_detail.html",
        {
            "post": post,
            "comentarios": comentarios,
            "form": form
        }
    )
