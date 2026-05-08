from django.db import models


class Postulacion(models.Model):
    ESTADO_POSTULADO = 'postulado'
    ESTADO_EN_REVISION = 'en_revision'
    ESTADO_ENTREVISTA = 'entrevista'
    ESTADO_EVALUACION = 'evaluacion'
    ESTADO_FINALISTA = 'finalista'
    ESTADO_RECHAZADO = 'rechazado'
    ESTADO_CONTRATADO = 'contratado'

    ESTADOS = [
        (ESTADO_POSTULADO, 'Postulado'),
        (ESTADO_EN_REVISION, 'En revisión'),
        (ESTADO_ENTREVISTA, 'Entrevista'),
        (ESTADO_EVALUACION, 'Evaluación'),
        (ESTADO_FINALISTA, 'Finalista'),
        (ESTADO_RECHAZADO, 'Rechazado'),
        (ESTADO_CONTRATADO, 'Contratado'),
    ]

    id_postulacion = models.BigAutoField(primary_key=True)
    id_candidato = models.ForeignKey('candidatos.Candidato', on_delete=models.CASCADE, db_column='id_candidato', related_name='postulaciones')
    id_vacante = models.ForeignKey('vacantes.Vacante', on_delete=models.CASCADE, db_column='id_vacante', related_name='postulaciones')
    estado = models.CharField(max_length=30, choices=ESTADOS, default=ESTADO_POSTULADO)
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True)

    class Meta:
        db_table = 'postulacion'
        ordering = ['-fecha_postulacion']
        constraints = [
            models.UniqueConstraint(fields=['id_candidato', 'id_vacante'], name='unique_candidato_vacante')
        ]

    def __str__(self):
        return f'{self.id_candidato} -> {self.id_vacante}'
