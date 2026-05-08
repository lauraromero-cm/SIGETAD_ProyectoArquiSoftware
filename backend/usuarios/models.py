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
