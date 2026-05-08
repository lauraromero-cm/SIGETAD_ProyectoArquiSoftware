from django.db import models


class Historial(models.Model):
    id_historial = models.BigAutoField(primary_key=True)
    id_postulacion = models.ForeignKey('postulaciones.Postulacion', on_delete=models.CASCADE, db_column='id_postulacion', related_name='historial')
    tipo = models.CharField(max_length=30)
    descripcion = models.TextField()
    id_usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='historial_registrado')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historial'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.tipo}: {self.descripcion[:40]}'
