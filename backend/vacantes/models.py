from django.db import models


class Vacante(models.Model):
    ESTADO_ABIERTA = 'abierta'
    ESTADO_CERRADA = 'cerrada'
    ESTADOS = [
        (ESTADO_ABIERTA, 'Abierta'),
        (ESTADO_CERRADA, 'Cerrada'),
    ]

    id_vacante = models.BigAutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    departamento = models.CharField(max_length=100)
    salario_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salario_maximo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    requisitos = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_ABIERTA)
    creado_por = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, db_column='creado_por', related_name='vacantes_creadas')

    class Meta:
        db_table = 'vacante'
        ordering = ['-id_vacante']

    def __str__(self):
        return self.titulo
