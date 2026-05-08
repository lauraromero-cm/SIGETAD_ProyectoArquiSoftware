from django.db import models


class Candidato(models.Model):
    id_candidato = models.BigAutoField(primary_key=True)
    id_usuario = models.OneToOneField('usuarios.Usuario', on_delete=models.CASCADE, db_column='id_usuario', related_name='candidato')
    nombre_completo = models.CharField(max_length=150)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    profesion = models.CharField(max_length=100, blank=True)
    experiencia_anios = models.IntegerField(default=0)
    cv = models.CharField(max_length=255, blank=True)
    foto_perfil = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'candidato'
        ordering = ['id_candidato']

    def __str__(self):
        return self.nombre_completo
