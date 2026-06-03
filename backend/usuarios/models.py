from django.db import models
from django.utils import timezone


class UsuarioManager(models.Manager):
    """Manager que excluye usuarios eliminados (soft delete)"""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def all_including_deleted(self):
        """Retorna todos los usuarios incluyendo eliminados"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Retorna solo usuarios eliminados"""
        return super().get_queryset().filter(is_deleted=True)


class Usuario(models.Model):
    ROL_ADMIN = 'admin'
    ROL_ANALISTA = 'analista'
    ROL_JEFE_AREA = 'jefe_area'
    ROL_CANDIDATO = 'candidato'

    ROLES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_ANALISTA, 'Analista de Selección'),
        (ROL_JEFE_AREA, 'Jefe de Área'),
        (ROL_CANDIDATO, 'Candidato'),
    ]

    ESTADO_ACTIVO = 'activo'
    ESTADO_INACTIVO = 'inactivo'

    ESTADOS = [
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_INACTIVO, 'Inactivo'),
    ]

    id_usuario = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=255)
    rol = models.CharField(max_length=30, choices=ROLES)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_ACTIVO)
    is_deleted = models.BooleanField(default=False, help_text='Soft delete: usuario marcado como eliminado')
    fecha_eliminacion = models.DateTimeField(null=True, blank=True, help_text='Fecha y hora de eliminación')
    
    objects = UsuarioManager()

    class Meta:
        db_table = 'usuario'
        ordering = ['id_usuario']
        indexes = [
            models.Index(fields=['is_deleted', 'estado'], name='idx_usuario_deleted_estado'),
            models.Index(fields=['correo', 'is_deleted'], name='idx_usuario_correo_deleted'),
        ]

    def __str__(self):
        status = ' (ELIMINADO)' if self.is_deleted else ''
        return f'{self.nombre} ({self.rol}){status}'
    
    def soft_delete(self):
        """Marca el usuario como eliminado (soft delete)"""
        self.is_deleted = True
        self.fecha_eliminacion = timezone.now()
        self.save(update_fields=['is_deleted', 'fecha_eliminacion'])
    
    def restore(self):
        """Restaura un usuario eliminado"""
        self.is_deleted = False
        self.fecha_eliminacion = None
        self.save(update_fields=['is_deleted', 'fecha_eliminacion'])


class LoginIntento(models.Model):
    RESULTADO_EXITO = 'exito'
    RESULTADO_FALLIDO = 'fallido'
    RESULTADO_BLOQUEADO = 'bloqueado'

    RESULTADOS = [
        (RESULTADO_EXITO, 'Éxito'),
        (RESULTADO_FALLIDO, 'Fallido'),
        (RESULTADO_BLOQUEADO, 'Bloqueado'),
    ]

    id_intento = models.BigAutoField(primary_key=True)
    correo = models.EmailField(max_length=100)
    resultado = models.CharField(max_length=20, choices=RESULTADOS)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_usuario', related_name='intentos_login')

    class Meta:
        db_table = 'login_intento'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['correo', '-fecha'], name='idx_login_correo_fecha'),
            models.Index(fields=['resultado', '-fecha'], name='idx_login_result_fecha'),
        ]
