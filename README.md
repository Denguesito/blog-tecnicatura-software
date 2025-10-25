# Blog Tecnicatura - mejoras de rendimiento

Acciones añadidas en el repo para mejorar rendimiento en móvil:

1. Configuración de WhiteNoise para servir `static` con compresión y cache-control.
   - Dependencia añadida: `whitenoise==6.5.0` (ver `requirements.txt`).
   - `settings.py` actualizado para usar `whitenoise.middleware.WhiteNoiseMiddleware` y `whitenoise.storage.CompressedManifestStaticFilesStorage`.

2. Script para generar variantes de imágenes responsivas:
   - `tools/resize_images.py` genera versiones `.webp` en `static/img/variants/` para las imágenes listadas.
   - Requiere `Pillow` (ya en `requirements.txt`).

3. Plantillas: añadidos `preconnect`, `loading="lazy"` y cambios para `srcset` (si hay variantes generadas).

Cómo generar variantes de imagen (local):

1. Instala dependencias en tu entorno:

```powershell
python -m pip install -r requirements.txt
```

2. Ejecuta el script para generar variantes:

```powershell
python tools\resize_images.py
```

3. Recolecta estáticos (si usas Django en producción):

```powershell
python manage.py collectstatic --noinput
```

Notas sobre despliegue en PythonAnywhere:
- PythonAnywhere puede servir archivos estáticos por sí mismo, pero no añade cache-control largo por defecto. WhiteNoise funciona bien en entornos WSGI y añadirá cabeceras adecuadas.
- Alternativa: poner Cloudflare/otro CDN delante para mejorar rendimiento global.

Siguientes pasos recomendados:
- Ejecutar el script y luego probar con Lighthouse (móvil) para medir mejora.
- Considerar afinado de calidad de imagen y añadir `srcset` para todas las imágenes dinámicas en artículos.

CKEditor y sanitización (Bleach)
--------------------------------
Se añadió soporte opcional para CKEditor (editor WYSIWYG) y Bleach para sanitizar HTML al guardar. Pasos rápidos:

1. Instalar dependencias (local o en el servidor):

```powershell
python -m pip install -r requirements.txt
```

2. Configurar si querés usar CKEditor: en el admin/form se usará `CKEditorUploadingWidget` para el campo `contenido`.

3. Bleach está configurado en `instituto/utils/sanitizers.py` y el formulario limpia el HTML antes de guardar.

4. Recuerda ejecutar `collectstatic` si añades nuevas static o por si cambias la configuración.

