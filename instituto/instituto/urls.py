from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from apps.blog.sitemaps import StaticViewSitemap, ArticuloSitemap
from . import views  # 👈 Importa tus vistas principales (index y Nosotros)

sitemaps = {
    'static': StaticViewSitemap,
    'articulos': ArticuloSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔹 Página principal y contacto
    path('', views.index, name='index'),
    path('contacto/', views.Nosotros, name='contacto'),

    # 🔹 Apps
    path('', include('apps.blog.urls')),
    path('comentarios/', include('apps.comentarios.urls')),
    path('usuarios/', include('apps.usuarios.urls')),

    # 🔹 CKEditor 5
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # 🔹 Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# 🔹 Archivos de medios (solo en desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

