import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from candidatos.models import Candidato
from usuarios.models import Usuario


FIXTURE_DIR = Path(__file__).resolve().parents[2] / 'fixtures'
DATA_FIXTURE = FIXTURE_DIR / 'datos.json'
UPLOADS_FIXTURE = FIXTURE_DIR / 'uploads' / 'candidatos'


class Command(BaseCommand):
    help = 'Exporta usuarios, perfiles de candidatos y archivos de CV/foto a fixtures versionables.'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=str(DATA_FIXTURE), help='Ruta donde guardar el fixture de datos.')

    def handle(self, *args, **options):
        path = Path(options['path'])
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'usuarios': [
                {
                    'id_usuario': usuario.id_usuario,
                    'nombre': usuario.nombre,
                    'correo': usuario.correo,
                    'contrasena': usuario.contrasena,
                    'rol': usuario.rol,
                    'estado': usuario.estado,
                }
                for usuario in Usuario.objects.order_by('id_usuario')
            ],
            'candidatos': [
                {
                    'id_candidato': candidato.id_candidato,
                    'id_usuario': candidato.id_usuario_id,
                    'nombre_completo': candidato.nombre_completo,
                    'email': candidato.email,
                    'telefono': candidato.telefono,
                    'profesion': candidato.profesion,
                    'experiencia_anios': candidato.experiencia_anios,
                    'cv': candidato.cv,
                    'foto_perfil': candidato.foto_perfil,
                }
                for candidato in Candidato.objects.order_by('id_candidato')
            ],
        }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        self._export_candidate_uploads()

        self.stdout.write(
            self.style.SUCCESS(
                f'Datos exportados: {len(data["usuarios"])} usuarios, '
                f'{len(data["candidatos"])} candidatos -> {path}'
            )
        )

    def _export_candidate_uploads(self):
        source = Path(settings.MEDIA_ROOT) / 'candidatos'
        if UPLOADS_FIXTURE.exists():
            shutil.rmtree(UPLOADS_FIXTURE)
        if source.exists():
            shutil.copytree(source, UPLOADS_FIXTURE)
