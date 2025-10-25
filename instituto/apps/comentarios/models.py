from django.db import models
from django.contrib.auth import get_user_model
from apps.blog.models import Articulo

User = get_user_model()

class Comentario(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name="comentarios")
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"

    def __str__(self):
        return f"Comentario de {self.autor} en {self.articulo}"
