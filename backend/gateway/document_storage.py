import hashlib
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import get_valid_filename


PDF_MIME_TYPES = {'application/pdf', 'application/x-pdf'}
PDF_MAGIC = b'%PDF-'
EICAR_MARKERS = (b'EICAR-STANDARD-ANTIVIRUS-TEST-FILE', b'X5O!P%@AP')


def validate_pdf_upload(uploaded_file: UploadedFile):
    max_bytes = settings.DOCUMENTOS_MAX_UPLOAD_BYTES
    if uploaded_file.size > max_bytes:
        raise ValueError(f'El archivo excede el tamaño máximo permitido de {max_bytes} bytes')

    original_name = uploaded_file.name or ''
    if not original_name.lower().endswith('.pdf'):
        raise ValueError('Solo se permiten archivos PDF')

    if uploaded_file.content_type and uploaded_file.content_type not in PDF_MIME_TYPES:
        raise ValueError('El content-type del archivo debe ser application/pdf')

    header = uploaded_file.read(8)
    uploaded_file.seek(0)
    if not header.startswith(PDF_MAGIC):
        raise ValueError('El archivo no parece ser un PDF válido')

    for chunk in uploaded_file.chunks():
        if any(marker in chunk for marker in EICAR_MARKERS):
            uploaded_file.seek(0)
            raise ValueError('El archivo no pasó el escaneo antivirus')
    uploaded_file.seek(0)


def save_document(uploaded_file: UploadedFile):
    validate_pdf_upload(uploaded_file)

    storage_dir = Path(settings.MEDIA_ROOT) / settings.DOCUMENTOS_STORAGE_DIR
    storage_dir.mkdir(parents=True, exist_ok=True)

    original_name = get_valid_filename(uploaded_file.name or 'documento.pdf')
    stored_name = f'{uuid.uuid4().hex}.pdf'
    absolute_path = storage_dir / stored_name
    relative_path = os.path.join(settings.DOCUMENTOS_STORAGE_DIR, stored_name)

    checksum = hashlib.sha256()
    with absolute_path.open('wb') as destination:
        for chunk in uploaded_file.chunks():
            checksum.update(chunk)
            destination.write(chunk)
    uploaded_file.seek(0)

    scan_saved_document(absolute_path)

    return {
        'nombre_original': original_name,
        'nombre_almacenado': stored_name,
        'ruta_relativa': relative_path,
        'content_type': 'application/pdf',
        'tamanio_bytes': uploaded_file.size,
        'checksum_sha256': checksum.hexdigest(),
        'absolute_path': absolute_path,
    }


def delete_saved_document(path):
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass


def scan_saved_document(path):
    clamscan = shutil.which('clamscan')
    if not clamscan:
        return

    try:
        result = subprocess.run(
            [clamscan, '--no-summary', str(path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        delete_saved_document(path)
        raise ValueError('No se pudo completar el escaneo antivirus') from exc
    if result.returncode == 1:
        delete_saved_document(path)
        raise ValueError('El archivo no pasó el escaneo antivirus')
    if result.returncode not in (0, 1):
        delete_saved_document(path)
        raise ValueError('No se pudo completar el escaneo antivirus')


def document_absolute_path(relative_path):
    base = Path(settings.MEDIA_ROOT).resolve()
    path = (base / relative_path).resolve()
    if base not in path.parents and path != base:
        raise ValueError('Ruta de documento inválida')
    return path
