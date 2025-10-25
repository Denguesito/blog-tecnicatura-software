from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from apps.blog.sitemaps import StaticViewSitemap, ArticuloSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'articulos': ArticuloSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.blog.urls')),
    path('comentarios/', include('apps.comentarios.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
