from django.db import models


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

    class Meta:
        db_table = 'usuario'
        ordering = ['id_usuario']

    def __str__(self):
        return f'{self.nombre} ({self.rol})'


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
