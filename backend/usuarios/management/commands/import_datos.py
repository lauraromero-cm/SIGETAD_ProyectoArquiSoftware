import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from candidatos.models import Candidato
from usuarios.models import Usuario


FIXTURE_DIR = Path(__file__).resolve().parents[2] / 'fixtures'
DATA_FIXTURE = FIXTURE_DIR / 'datos.json'
UPLOADS_FIXTURE = FIXTURE_DIR / 'uploads' / 'candidatos'


class Command(BaseCommand):
    help = 'Importa usuarios, perfiles de candidatos y archivos de CV/foto desde fixtures versionables.'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=str(DATA_FIXTURE), help='Ruta del fixture de datos.')

    def handle(self, *args, **options):
        path = Path(options['path'])
        data = self._load_data(path)
        if data is None:
            self.stdout.write(f'Fixture de datos no encontrado: {path}')
            return

        with transaction.atomic():
            usuarios_importados, usuarios_actualizados = self._import_users(data.get('usuarios', []))
            candidatos_importados, candidatos_actualizados = self._import_candidates(data.get('candidatos', []))
            self._reset_sequence(Usuario)
            self._reset_sequence(Candidato)

        archivos = self._import_candidate_uploads()
        self.stdout.write(
            self.style.SUCCESS(
                f'Usuarios importados: {usuarios_importados}. Usuarios actualizados: {usuarios_actualizados}. '
                f'Candidatos importados: {candidatos_importados}. Candidatos actualizados: {candidatos_actualizados}. '
                f'Archivos restaurados: {archivos}.'
            )
        )

    def _load_data(self, path):
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
        return None

    def _import_users(self, usuarios):
        created = 0
        updated = 0
        for data in usuarios:
            user_id = data.get('id_usuario')
            correo = data['correo']
            defaults = {
                'nombre': data['nombre'],
                'correo': correo,
                'contrasena': data['contrasena'],
                'rol': data['rol'],
                'estado': data['estado'],
            }

            usuario = Usuario.objects.filter(id_usuario=user_id).first() if user_id else None
            if usuario is None:
                usuario = Usuario.objects.filter(correo=correo).first()

            if usuario is None:
                if user_id:
                    defaults['id_usuario'] = user_id
                Usuario.objects.create(**defaults)
                created += 1
            else:
                for field, value in defaults.items():
                    setattr(usuario, field, value)
                usuario.save(update_fields=list(defaults.keys()))
                updated += 1
        return created, updated

    def _import_candidates(self, candidatos):
        created = 0
        updated = 0
        for data in candidatos:
            candidato_id = data.get('id_candidato')
            defaults = {
                'id_usuario_id': data['id_usuario'],
                'nombre_completo': data['nombre_completo'],
                'email': data['email'],
                'telefono': data.get('telefono', ''),
                'profesion': data.get('profesion', ''),
                'experiencia_anios': data.get('experiencia_anios') or 0,
                'cv': data.get('cv', ''),
                'foto_perfil': data.get('foto_perfil', ''),
            }

            candidato = Candidato.objects.filter(id_candidato=candidato_id).first() if candidato_id else None
            if candidato is None:
                candidato = Candidato.objects.filter(id_usuario_id=data['id_usuario']).first()

            if candidato is None:
                if candidato_id:
                    defaults['id_candidato'] = candidato_id
                Candidato.objects.create(**defaults)
                created += 1
            else:
                for field, value in defaults.items():
                    setattr(candidato, field, value)
                candidato.save(update_fields=list(defaults.keys()))
                updated += 1
        return created, updated

    def _import_candidate_uploads(self):
        if not UPLOADS_FIXTURE.exists():
            return 0
        target = Path(settings.MEDIA_ROOT) / 'candidatos'
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(UPLOADS_FIXTURE, target)
        return sum(1 for item in target.rglob('*') if item.is_file())

    def _reset_sequence(self, model):
        table = model._meta.db_table
        pk = model._meta.pk.column
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT setval(pg_get_serial_sequence(%s, %s), '
                f'COALESCE((SELECT MAX("{pk}") FROM "{table}"), 1), '
                f'EXISTS(SELECT 1 FROM "{table}"))',
                [table, pk],
            )
