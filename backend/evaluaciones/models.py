from django.db import models


class Evaluacion(models.Model):
    id_evaluacion = models.BigAutoField(primary_key=True)
    id_postulacion = models.OneToOneField('postulaciones.Postulacion', on_delete=models.CASCADE, db_column='id_postulacion', related_name='evaluacion')
    id_usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='evaluaciones')
    calificacion = models.IntegerField()
    comentarios = models.TextField(blank=True)

    class Meta:
        db_table = 'evaluacion'
        ordering = ['-id_evaluacion']

    def __str__(self):
        return f'Evaluación {self.id_evaluacion}'
