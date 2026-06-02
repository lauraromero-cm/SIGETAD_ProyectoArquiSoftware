from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from usuarios.models import Usuario
from candidatos.models import Candidato
from vacantes.models import Vacante
from postulaciones.models import Postulacion
from historial.models import Historial


class Command(BaseCommand):
    help = 'Crea datos iniciales para probar SIGETAD.'

    def handle(self, *args, **options):
        admin = self.get_or_create_user('Administrador SIGETAD', 'admin@firmafast.cl', 'admin')
        analista = self.get_or_create_user('Laura Analista', 'analista@firmafast.cl', 'analista')
        jefe = self.get_or_create_user('Jefe de Área TI', 'jefe@firmafast.cl', 'jefe_area')
        candidato_user = self.get_or_create_user('Candidato Demo', 'candidato@correo.cl', 'candidato')

        candidato, _ = Candidato.objects.get_or_create(
            id_usuario=candidato_user,
            defaults={
                'nombre_completo': 'Candidato Demo',
                'email': 'candidato@correo.cl',
                'telefono': '+56 9 1234 5678',
                'profesion': 'Desarrollador Full Stack',
                'experiencia_anios': 3,
                'cv': '',
                'foto_perfil': '',
            },
        )

        vacante1, _ = Vacante.objects.get_or_create(
            titulo='Desarrollador Backend Django',
            defaults={
                'descripcion': 'Desarrollo de servicios backend para plataforma SaaS.',
                'departamento': 'Tecnología',
                'salario_minimo': 1200000,
                'salario_maximo': 1800000,
                'requisitos': 'Python, Django, PostgreSQL, APIs y buenas prácticas.',
                'estado': 'abierta',
                'creado_por': analista,
            },
        )
        Vacante.objects.get_or_create(
            titulo='Analista QA Automatizador',
            defaults={
                'descripcion': 'Diseño y ejecución de pruebas funcionales y automatizadas.',
                'departamento': 'Producto',
                'salario_minimo': 1000000,
                'salario_maximo': 1500000,
                'requisitos': 'Testing, Selenium/Cypress, documentación y criterio de calidad.',
                'estado': 'abierta',
                'creado_por': analista,
            },
        )

        postulacion, created = Postulacion.objects.get_or_create(
            id_candidato=candidato,
            id_vacante=vacante1,
            defaults={'estado': 'postulado', 'notas': 'Postulación de prueba creada automáticamente.'},
        )
        if created:
            Historial.objects.create(
                id_postulacion=postulacion,
                tipo='postulacion',
                descripcion='Postulación inicial de prueba.',
                id_usuario=candidato_user,
            )

        self.stdout.write(self.style.SUCCESS('Datos iniciales listos.'))

    def get_or_create_user(self, nombre, correo, rol):
        user, created = Usuario.objects.get_or_create(
            correo=correo,
            defaults={
                'nombre': nombre,
                'contrasena': make_password('admin123'),
                'rol': rol,
                'estado': 'activo',
            },
        )
        if created:
            self.stdout.write(f'Usuario creado: {correo} / admin123')
        return user
