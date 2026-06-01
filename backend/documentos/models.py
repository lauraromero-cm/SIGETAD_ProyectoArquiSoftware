from django.db import models


class Documento(models.Model):
    ESTADO_DISPONIBLE = 'disponible'
    ESTADO_ELIMINADO = 'eliminado'

    ESTADOS = [
        (ESTADO_DISPONIBLE, 'Disponible'),
        (ESTADO_ELIMINADO, 'Eliminado'),
    ]

    id_documento = models.BigAutoField(primary_key=True)
    nombre_original = models.CharField(max_length=255)
    nombre_almacenado = models.CharField(max_length=255, unique=True)
    ruta_relativa = models.CharField(max_length=500)
    content_type = models.CharField(max_length=100, default='application/pdf')
    tamanio_bytes = models.PositiveBigIntegerField()
    checksum_sha256 = models.CharField(max_length=64)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_DISPONIBLE)
    id_usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='documentos_subidos')
    id_postulacion = models.ForeignKey(
        'postulaciones.Postulacion',
        on_delete=models.CASCADE,
        db_column='id_postulacion',
        related_name='documentos',
        null=True,
        blank=True,
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documento'
        ordering = ['-fecha_subida']
        indexes = [
            models.Index(fields=['id_usuario', '-fecha_subida'], name='idx_doc_usuario_fecha'),
            models.Index(fields=['id_postulacion', '-fecha_subida'], name='idx_doc_post_fecha'),
            models.Index(fields=['checksum_sha256'], name='idx_doc_checksum'),
        ]

    def __str__(self):
        return self.nombre_original


class DocumentoAuditoria(models.Model):
    ACCION_SUBIDA = 'subida'
    ACCION_URL_GENERADA = 'url_generada'
    ACCION_DESCARGA = 'descarga'

    ACCIONES = [
        (ACCION_SUBIDA, 'Subida'),
        (ACCION_URL_GENERADA, 'URL generada'),
        (ACCION_DESCARGA, 'Descarga'),
    ]

    id_auditoria = models.BigAutoField(primary_key=True)
    id_documento = models.ForeignKey(Documento, on_delete=models.CASCADE, db_column='id_documento', related_name='auditoria')
    id_usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='auditoria_documentos')
    accion = models.CharField(max_length=30, choices=ACCIONES)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'documento_auditoria'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['id_documento', '-fecha'], name='idx_doc_aud_doc_fecha'),
            models.Index(fields=['id_usuario', '-fecha'], name='idx_doc_aud_usr_fecha'),
            models.Index(fields=['accion', '-fecha'], name='idx_doc_aud_acc_fecha'),
        ]

    def __str__(self):
        return f'{self.accion}: {self.id_documento_id}'
