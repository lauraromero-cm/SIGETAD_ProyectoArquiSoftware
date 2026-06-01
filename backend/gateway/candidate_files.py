import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import get_valid_filename


CV_TYPES = {
    'application/pdf': ('.pdf', b'%PDF-'),
    'application/msword': ('.doc', b'\xd0\xcf\x11\xe0'),
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ('.docx', b'PK\x03\x04'),
}
PHOTO_TYPES = {
    'image/jpeg': (('.jpg', '.jpeg'), (b'\xff\xd8\xff',)),
    'image/png': (('.png',), (b'\x89PNG\r\n\x1a\n',)),
    'image/gif': (('.gif',), (b'GIF87a', b'GIF89a')),
    'image/bmp': (('.bmp',), (b'BM',)),
    'image/webp': (('.webp',), (b'RIFF',)),
    'image/tiff': (('.tif', '.tiff'), (b'II*\x00', b'MM\x00*')),
}
MAX_CV_BYTES = 10 * 1024 * 1024
MAX_PHOTO_BYTES = 5 * 1024 * 1024


def _validate_magic(uploaded_file, expected):
    header = uploaded_file.read(12)
    uploaded_file.seek(0)
    markers = expected if isinstance(expected, tuple) else (expected,)
    if not any(header.startswith(marker) for marker in markers):
        raise ValueError('El archivo no coincide con el formato declarado')


def _save_candidate_file(uploaded_file: UploadedFile, user_id, subdir, allowed_types, max_bytes):
    if uploaded_file.size > max_bytes:
        raise ValueError(f'El archivo excede el tamaño máximo permitido de {max_bytes} bytes')

    content_type = uploaded_file.content_type
    if content_type not in allowed_types:
        raise ValueError('Formato de archivo no permitido')

    extensions, magic = allowed_types[content_type]
    if isinstance(extensions, str):
        extensions = (extensions,)
    extension = extensions[0]
    original_name = get_valid_filename(uploaded_file.name or f'archivo{extension}')
    if not original_name.lower().endswith(extensions):
        raise ValueError(f'La extensión del archivo debe ser {", ".join(extensions)}')

    _validate_magic(uploaded_file, magic)

    storage_dir = Path(settings.MEDIA_ROOT) / 'candidatos' / str(user_id) / subdir
    storage_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f'{uuid.uuid4().hex}{extension}'
    absolute_path = storage_dir / stored_name
    with absolute_path.open('wb') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    uploaded_file.seek(0)

    return {
        'nombre_original': original_name,
        'ruta_relativa': os.path.join('candidatos', str(user_id), subdir, stored_name),
    }


def save_candidate_cv(uploaded_file, user_id):
    return _save_candidate_file(uploaded_file, user_id, 'cv', CV_TYPES, MAX_CV_BYTES)


def save_candidate_photo(uploaded_file, user_id):
    return _save_candidate_file(uploaded_file, user_id, 'foto', PHOTO_TYPES, MAX_PHOTO_BYTES)


def delete_candidate_file(relative_path):
    if not relative_path:
        return
    try:
        path = (Path(settings.MEDIA_ROOT) / relative_path).resolve()
        base = Path(settings.MEDIA_ROOT).resolve()
        if base in path.parents:
            path.unlink(missing_ok=True)
    except OSError:
        pass
