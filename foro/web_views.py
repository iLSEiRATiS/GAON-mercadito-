from django.shortcuts import render
from django.core.paginator import Paginator
from foro.models import Comentario
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from .forms import PostForm
from django.views.decorators.http import require_http_methods



def foro_home(request):
    """Lista los comentarios con paginación.

    Parámetros GET:
    - page: número de página (1-based)

    Devuelve `page_obj` en el contexto y renderiza `foro/home.html`.
    """
    qs = Comentario.objects.select_related('autor', 'producto').order_by('-creado_en')
    paginator = Paginator(qs, 20)  # 20 comentarios por página
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    return render(request, 'foro/home.html', {'page_obj': page_obj})


def posts_list(request):
    """Lista de publicaciones tipo foro (Posts) con paginación."""
    qs = Post.objects.select_related('autor', 'producto').order_by('-creado_en')
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page') or 1)
    return render(request, 'foro/posts_list.html', {'page_obj': page_obj})


def post_detail(request, pk: int):
    post = get_object_or_404(Post.objects.select_related('autor', 'producto'), pk=pk)
    return render(request, 'foro/post_detail.html', {'post': post})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            messages.success(request, 'Publicación creada correctamente.')
            return redirect('foro:post-detail' if False else 'foro:posts')
    else:
        form = PostForm()

    return render(request, 'foro/post_create.html', {'form': form})


@login_required
def post_edit(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if not (user.is_staff or user.is_superuser or post.autor_id == user.id):
        return redirect('/account/')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicación actualizada correctamente.')
            return redirect('foro:post-detail', pk=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'foro/post_create.html', {'form': form, 'is_edit': True, 'post': post})


@login_required
def post_delete(request, pk: int):
    """Confirmar y eliminar un Post.

    GET -> mostrar formulario de confirmación
    POST -> eliminar y redirigir a /account/
    """
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if not (user.is_staff or user.is_superuser or post.autor_id == user.id):
        return redirect('/account/')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Publicación eliminada.')
        return redirect('/account/')

    return render(request, 'foro/post_confirm_delete.html', {'post': post})


@login_required
def comentario_edit(request, pk: int):
    c = get_object_or_404(Comentario, pk=pk)
    user = request.user
    if not (user.is_staff or user.is_superuser or c.autor_id == user.id):
        return redirect('/account/')

    if request.method == 'POST':
        texto = (request.POST.get('texto') or '').strip()
        if texto:
            c.texto = texto
            c.save()
            messages.success(request, 'Comentario actualizado.')
            return redirect('/account/')
        else:
            messages.error(request, 'El texto no puede estar vacío.')

    return render(request, 'foro/comentario_edit.html', {'comentario': c})


@login_required
def comentario_delete(request, pk: int):
    """Confirmar y eliminar un Comentario.

    GET -> mostrar confirmación
    POST -> eliminar y redirigir a /account/
    """
    c = get_object_or_404(Comentario, pk=pk)
    user = request.user
    if not (user.is_staff or user.is_superuser or c.autor_id == user.id):
        return redirect('/account/')

    if request.method == 'POST':
        c.delete()
        messages.success(request, 'Comentario eliminado.')
        return redirect('/account/')

    return render(request, 'foro/comentario_confirm_delete.html', {'comentario': c})
