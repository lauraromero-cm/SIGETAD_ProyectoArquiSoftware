from django.db import models


class Historial(models.Model):
    TIPO_POSTULACION = 'postulacion'
    TIPO_ESTADO = 'estado'
    TIPO_EVALUACION = 'evaluacion'
    TIPO_CAMBIO_CAMPO = 'cambio_campo'
    TIPO_EVENTO = 'evento'
    
    TIPOS = [
        (TIPO_POSTULACION, 'Postulación'),
        (TIPO_ESTADO, 'Cambio de Estado'),
        (TIPO_EVALUACION, 'Evaluación'),
        (TIPO_CAMBIO_CAMPO, 'Cambio de Campo'),
        (TIPO_EVENTO, 'Evento Manual'),
    ]
    
    ENTIDAD_POSTULACION = 'postulacion'
    ENTIDAD_VACANTE = 'vacante'
    ENTIDAD_CANDIDATO = 'candidato'
    ENTIDAD_USUARIO = 'usuario'
    ENTIDAD_EVALUACION = 'evaluacion'
    
    ENTIDADES = [
        (ENTIDAD_POSTULACION, 'Postulación'),
        (ENTIDAD_VACANTE, 'Vacante'),
        (ENTIDAD_CANDIDATO, 'Candidato'),
        (ENTIDAD_USUARIO, 'Usuario'),
        (ENTIDAD_EVALUACION, 'Evaluación'),
    ]

    id_historial = models.BigAutoField(primary_key=True)
    id_postulacion = models.ForeignKey('postulaciones.Postulacion', on_delete=models.CASCADE, db_column='id_postulacion', related_name='historial', null=True, blank=True)
    tipo = models.CharField(max_length=30, choices=TIPOS)
    descripcion = models.TextField()
    id_usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, db_column='id_usuario', related_name='historial_registrado')
    fecha = models.DateTimeField(auto_now_add=True)
    
    # Campos nuevos para auditoría mejorada
    cambios_detalles = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text='Detalles de cambios: {campo, valor_anterior, valor_nuevo}'
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text='Soft delete: no se elimina físicamente'
    )
    fecha_eliminacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha cuando se marcó como eliminado'
    )
    id_entidad_tipo = models.CharField(
        max_length=50,
        default=ENTIDAD_POSTULACION,
        choices=ENTIDADES,
        help_text='Tipo de entidad que se audita'
    )
    id_entidad_referencia = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='ID de la entidad (ej: id_vacante, id_candidato)'
    )

    class Meta:
        db_table = 'historial'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['id_usuario', '-fecha'], name='idx_hist_usuario_fecha'),
            models.Index(fields=['id_entidad_tipo', 'id_entidad_referencia', '-fecha'], name='idx_hist_entidad_fecha'),
            models.Index(fields=['tipo', '-fecha'], name='idx_hist_tipo_fecha'),
        ]

    def __str__(self):
        return f'{self.tipo}: {self.descripcion[:40]}'
    
    def marcar_eliminado(self, usuario_id=None):
        """Soft delete: marca como eliminado sin borrar físicamente"""
        from django.utils import timezone
        self.is_deleted = True
        self.fecha_eliminacion = timezone.now()
        self.save(update_fields=['is_deleted', 'fecha_eliminacion'])
