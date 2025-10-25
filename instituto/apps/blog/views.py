from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Articulo, Categoria, ImagenArticulo
from .forms import ArticuloForm
from django.db.models import Sum
from apps.comentarios.models import Comentario
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from apps.comentarios.forms import ComentarioForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.text import get_valid_filename
from django.conf import settings
import os


class ArticuloListView(ListView):
    model = Articulo
    template_name = 'blog/lista_articulos.html'
    context_object_name = 'articulos'
    paginate_by = 4  # 👈 Paginación (2 artículos por página)

    def get_queryset(self):
        queryset = super().get_queryset()

        # 👇 Optimización de queries
        queryset = queryset.select_related("categoria", "autor").prefetch_related("imagenes")
        queryset = queryset.order_by('-fecha_publicacion')

        categoria_id = self.request.GET.get('categoria')
        ordenar_por = self.request.GET.get('ordenar_por')

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        if ordenar_por == 'asc':
            queryset = queryset.order_by('visitas')
        elif ordenar_por == 'desc':
            queryset = queryset.order_by('-visitas')
        elif ordenar_por == 'fecha_asc':
            queryset = queryset.order_by('fecha_publicacion')
        elif ordenar_por == 'fecha_desc':
            queryset = queryset.order_by('-fecha_publicacion')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context


class ArticuloDetailView(DetailView):
    model = Articulo
    template_name = 'blog/detalle_articulo.html'
    context_object_name = 'articulo'

    def get_object(self):
        articulo = super().get_object()
        articulo.visitas += 1
        articulo.save(update_fields=['visitas'])
        return articulo

    def get_queryset(self):
        # Optimización de queries
        return super().get_queryset().select_related(
            "categoria", "autor"
        ).prefetch_related("imagenes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_actual'] = self.request.user
        # Prefetch de comentarios
        context['comentarios'] = Comentario.objects.filter(
            articulo=self.object
        ).select_related("autor")
        # Pasamos form vacío (lo usa el template para hacer POST al CreateView de comentarios)
        context['form'] = ComentarioForm()
        return context

    def post(self, request, *args, **kwargs):
        articulo = self.get_object()
        contenido = request.POST.get('contenido')
        if contenido and request.user.is_authenticated:
            Comentario.objects.create(
                contenido=contenido,
                articulo=articulo,
                autor=request.user
            )
        return self.get(request, *args, **kwargs)


class ArticuloCreateView(LoginRequiredMixin, CreateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'blog/crear_articulo.html'
    success_url = reverse_lazy('blog:lista_articulos')

    def form_valid(self, form):
        form.instance.autor = self.request.user

        # Validar archivos recibidos (tipo y tamaño)
        archivos = self.request.FILES.getlist('imagenes')
        errores = []
        tipos_validos = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        max_size = 5 * 1024 * 1024

        for f in archivos:
            if f.content_type not in tipos_validos:
                errores.append(f"{f.name}: tipo de archivo no permitido ({f.content_type}).")
            if f.size > max_size:
                errores.append(f"{f.name}: excede 5MB.")

        if errores:
            # Anexar errores genéricos al formulario y re-renderizar
            form.add_error('titulo', 'Errores en archivos: ' + '; '.join(errores))
            return self.form_invalid(form)

        # Si todo está bien, guardar el objeto y luego las imágenes
        response = super().form_valid(form)
        for archivo in archivos:
            ImagenArticulo.objects.create(articulo=self.object, imagen=archivo)
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class ArticuloUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Articulo
    form_class = ArticuloForm
    template_name = 'blog/editar_articulo.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        for archivo in self.request.FILES.getlist('imagenes'):
            ImagenArticulo.objects.create(articulo=self.object, imagen=archivo)
        return response

    def test_func(self):
        return self.get_object().puede_editar(self.request.user)

    def get_success_url(self):
        return reverse_lazy('blog:detalle_articulo', kwargs={'pk': self.object.pk})
    

@login_required
def eliminar_imagen_articulo(request, pk):
    """
    Elimina una imagen de un artículo mediante AJAX.
    """
    try:
        imagen = ImagenArticulo.objects.get(pk=pk)
        if imagen.articulo.puede_editar(request.user):
            imagen.delete()
            return JsonResponse({'ok': True})
        else:
            return JsonResponse({'ok': False, 'error': 'No tienes permisos para eliminar esta imagen.'})
    except ImagenArticulo.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Imagen no encontrada.'})


class ArticuloDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Articulo
    template_name = 'blog/eliminar_articulo.html'
    success_url = reverse_lazy('blog:lista_articulos')

    def test_func(self):
        return self.get_object().puede_editar(self.request.user)


class PaginaPrincipalView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_visitas = Articulo.objects.aggregate(total_visitas=Sum('visitas'))['total_visitas'] or 0
        context['total_visitas'] = total_visitas
        return context


@login_required
@require_POST
def ckeditor5_upload(request):
    """Endpoint simple para recibir subidas desde CKEditor5 SimpleUploadAdapter.

    Espera un campo 'upload' en multipart/form-data y devuelve JSON {"url": "..."}.
    Requiere usuario autenticado para evitar subidas anónimas.
    """
    upload = request.FILES.get('upload')
    if not upload:
        return JsonResponse({'error': 'No file uploaded.'}, status=400)

    # construir ruta dentro de MEDIA_ROOT: uploads/YYYY/MM/DD/filename
    today = timezone.now()
    folder = os.path.join('uploads', str(today.year), f"{today.month:02}", f"{today.day:02}")
    filename = get_valid_filename(upload.name)
    save_path = os.path.join(folder, filename)

    # Asegurar no sobrescribir: default_storage.save hará unique name si existe
    saved_path = default_storage.save(save_path, upload)
    url = settings.MEDIA_URL.rstrip('/') + '/' + saved_path.replace('\\', '/')
    return JsonResponse({'url': url}, status=201)
