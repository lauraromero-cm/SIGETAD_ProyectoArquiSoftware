import mimetypes
from pathlib import Path

from django.conf import settings
from django.core import signing
from django.http import FileResponse, Http404, JsonResponse
from django.urls import reverse

from bus.bus_client import call_service
from .auth import make_token, verify_token
from .utils import api_view, parse_json, ok, require_auth
from .candidate_files import delete_candidate_file, save_candidate_cv, save_candidate_photo
from .document_storage import delete_saved_document, document_absolute_path, save_document


@api_view(['GET'])
def health(request):
    return ok({'status': 'ok', 'app': 'FirmaFast - SIGETAD'})


@api_view(['POST'])
def login(request):
    data = parse_json(request)
    data['ip'] = request.META.get('REMOTE_ADDR')
    data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
    user = call_service('USUAR', 'login', data)
    token = make_token(user)
    return ok({'token': token, 'user': user})


@api_view(['POST'])
def register_candidate(request):
    data = parse_json(request)
    result = call_service('USUAR', 'registrar_candidato_usuario', data)
    user = result['usuario']
    token = make_token(user)
    return ok({'token': token, 'user': user, 'candidato': result['candidato']}, status=201)


@api_view(['GET', 'POST'])
@require_auth
def usuarios(request):
    if request.method == 'GET':
        return ok(call_service('USUAR', 'listar_usuarios', user=request.current_user))
    return ok(call_service('USUAR', 'crear_usuario', parse_json(request), request.current_user), status=201)


@api_view(['POST'])
@require_auth
def usuario_estado(request, id_usuario):
    data = parse_json(request)
    data['id_usuario'] = id_usuario
    return ok(call_service('USUAR', 'cambiar_estado', data, request.current_user))


@api_view(['DELETE', 'POST'])
@require_auth
def usuario_delete(request, id_usuario):
    data = parse_json(request) if request.method == 'POST' else {}
    data['id_usuario'] = id_usuario
    return ok(call_service('USUAR', 'eliminar_usuario', data, request.current_user))


@api_view(['GET', 'POST'])
@require_auth
def vacantes(request):
    if request.method == 'GET':
        solo_abiertas = request.GET.get('solo_abiertas', 'true').lower() != 'false'
        return ok(call_service('VACAN', 'listar_vacantes', {'solo_abiertas': solo_abiertas}, request.current_user))
    return ok(call_service('VACAN', 'crear_vacante', parse_json(request), request.current_user), status=201)


@api_view(['GET', 'PUT'])
@require_auth
def vacante_detail(request, id_vacante):
    if request.method == 'GET':
        return ok(call_service('VACAN', 'obtener_vacante', {'id_vacante': id_vacante}, request.current_user))
    data = parse_json(request)
    data['id_vacante'] = id_vacante
    return ok(call_service('VACAN', 'editar_vacante', data, request.current_user))


@api_view(['POST'])
@require_auth
def vacante_cerrar(request, id_vacante):
    return ok(call_service('VACAN', 'cerrar_vacante', {'id_vacante': id_vacante}, request.current_user))


@api_view(['GET'])
@require_auth
def candidatos(request):
    return ok(call_service('CANDI', 'listar_candidatos', {'q': request.GET.get('q')}, request.current_user))


@api_view(['GET'])
@require_auth
def candidato_url_archivo(request, id_candidato, tipo):
    call_service('CANDI', 'obtener_archivo_perfil', {
        'id_candidato': id_candidato,
        'tipo': tipo,
    }, request.current_user)
    token = signing.dumps(
        {'id_candidato': id_candidato, 'tipo': tipo, 'user': request.current_user},
        salt='candidate-file',
        compress=True,
    )
    path = reverse('candidato-archivo', kwargs={'id_candidato': id_candidato, 'tipo': tipo})
    return ok({
        'url': request.build_absolute_uri(f'{path}?token={token}'),
        'download_url': request.build_absolute_uri(f'{path}?token={token}&download=1'),
        'expira_en_segundos': settings.CANDIDATE_FILE_TOKEN_SECONDS,
    })


@api_view(['GET'])
def candidato_archivo(request, id_candidato, tipo):
    token = request.GET.get('token', '')
    try:
        payload = signing.loads(token, salt='candidate-file', max_age=settings.CANDIDATE_FILE_TOKEN_SECONDS)
    except signing.BadSignature as exc:
        raise ValueError('Token inválido o expirado') from exc

    if int(payload.get('id_candidato')) != int(id_candidato) or payload.get('tipo') != tipo:
        raise ValueError('Token no corresponde al archivo solicitado')
    user = payload.get('user') or {}

    archivo = call_service('CANDI', 'obtener_archivo_perfil', {
        'id_candidato': id_candidato,
        'tipo': tipo,
    }, user)

    base = Path(settings.MEDIA_ROOT).resolve()
    absolute_path = (base / archivo['ruta_relativa']).resolve()
    if base not in absolute_path.parents or not absolute_path.exists():
        raise Http404('Archivo no encontrado')

    content_type, _ = mimetypes.guess_type(str(absolute_path))
    as_attachment = request.GET.get('download', '').lower() in ('1', 'true', 'yes')
    call_service('CANDI', 'registrar_acceso_archivo_perfil', {
        'id_candidato': id_candidato,
        'tipo': tipo,
        'accion': 'descarga' if as_attachment else 'visualización',
    }, user)
    return FileResponse(
        absolute_path.open('rb'),
        as_attachment=as_attachment,
        filename=absolute_path.name,
        content_type=content_type or 'application/octet-stream',
    )


@api_view(['GET', 'POST'])
@require_auth
def candidato_me(request):
    if request.method == 'GET':
        return ok(call_service('CANDI', 'mi_perfil', user=request.current_user))
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        data = {
            'nombre_completo': request.POST.get('nombre_completo', ''),
            'email': request.POST.get('email', ''),
            'telefono': request.POST.get('telefono', ''),
            'profesion': request.POST.get('profesion', ''),
            'experiencia_anios': request.POST.get('experiencia_anios', ''),
        }
        saved_files = []
        if request.FILES.get('cv'):
            cv = save_candidate_cv(request.FILES['cv'], request.current_user['id_usuario'])
            data['cv'] = cv['ruta_relativa']
            saved_files.append(cv['ruta_relativa'])
        if request.FILES.get('foto_perfil'):
            foto = save_candidate_photo(request.FILES['foto_perfil'], request.current_user['id_usuario'])
            data['foto_perfil'] = foto['ruta_relativa']
            saved_files.append(foto['ruta_relativa'])
        try:
            return ok(call_service('CANDI', 'guardar_perfil', data, request.current_user))
        except Exception:
            for relative_path in saved_files:
                delete_candidate_file(relative_path)
            raise
    return ok(call_service('CANDI', 'guardar_perfil', parse_json(request), request.current_user))


@api_view(['GET', 'POST'])
@require_auth
def postulaciones(request):
    if request.method == 'GET':
        data = {
            'id_vacante': request.GET.get('id_vacante'),
            'estado': request.GET.get('estado'),
            'q': request.GET.get('q'),
        }
        return ok(call_service('POSTU', 'listar_postulaciones', data, request.current_user))
    return ok(call_service('POSTU', 'postular', parse_json(request), request.current_user), status=201)


@api_view(['GET'])
@require_auth
def postulacion_detail(request, id_postulacion):
    return ok(call_service('POSTU', 'obtener_postulacion', {'id_postulacion': id_postulacion}, request.current_user))


@api_view(['POST'])
@require_auth
def postulacion_estado(request, id_postulacion):
    data = parse_json(request)
    data['id_postulacion'] = id_postulacion
    return ok(call_service('POSTU', 'actualizar_estado', data, request.current_user))


@api_view(['GET', 'POST'])
@require_auth
def evaluaciones(request):
    if request.method == 'GET':
        return ok(call_service('EVALU', 'listar_evaluaciones', {'id_postulacion': request.GET.get('id_postulacion')}, request.current_user))
    return ok(call_service('EVALU', 'registrar_evaluacion', parse_json(request), request.current_user), status=201)


@api_view(['GET', 'POST'])
@require_auth
def historial(request):
    if request.method == 'GET':
        filters = {
            'id_postulacion': request.GET.get('id_postulacion'),
            'tipo': request.GET.get('tipo'),
            'q': request.GET.get('q'),
            'id_usuario': request.GET.get('id_usuario'),
            'fecha_desde': request.GET.get('fecha_desde'),
            'fecha_hasta': request.GET.get('fecha_hasta'),
            'id_entidad': request.GET.get('id_entidad'),
            'tipo_entidad': request.GET.get('tipo_entidad'),
            'orden': request.GET.get('orden', '-fecha'),
        }
        # Remover valores None para no confundir al handler
        filters = {k: v for k, v in filters.items() if v is not None}
        return ok(call_service('HISTO', 'listar_historial', filters, request.current_user))
    return ok(call_service('HISTO', 'registrar_evento', parse_json(request), request.current_user), status=201)


@api_view(['GET', 'POST'])
@require_auth
def documentos(request):
    if request.method == 'GET':
        filters = {
            'id_postulacion': request.GET.get('id_postulacion'),
            'id_usuario': request.GET.get('id_usuario'),
            'q': request.GET.get('q'),
        }
        filters = {k: v for k, v in filters.items() if v}
        return ok(call_service('DOCUM', 'listar_documentos', filters, request.current_user))

    uploaded_file = request.FILES.get('archivo') or request.FILES.get('file')
    if not uploaded_file:
        raise ValueError('Debes enviar un archivo PDF en el campo archivo')

    saved = save_document(uploaded_file)
    try:
        data = {
            'id_postulacion': request.POST.get('id_postulacion') or None,
            'nombre_original': saved['nombre_original'],
            'nombre_almacenado': saved['nombre_almacenado'],
            'ruta_relativa': saved['ruta_relativa'],
            'content_type': saved['content_type'],
            'tamanio_bytes': saved['tamanio_bytes'],
            'checksum_sha256': saved['checksum_sha256'],
        }
        documento = call_service('DOCUM', 'registrar_documento', data, request.current_user)
    except Exception:
        delete_saved_document(saved['absolute_path'])
        raise

    return ok(documento, status=201)


@api_view(['GET'])
@require_auth
def documento_url_descarga(request, id_documento):
    documento = call_service('DOCUM', 'registrar_url_generada', {
        'id_documento': id_documento,
        'expira_en_segundos': settings.DOCUMENTOS_DOWNLOAD_TOKEN_SECONDS,
    }, request.current_user)
    token = signing.dumps(
        {'id_documento': id_documento, 'user': request.current_user},
        salt='documento-download',
        compress=True,
    )
    path = reverse('documento-descarga', kwargs={'id_documento': id_documento})
    return ok({
        'documento': documento,
        'url': request.build_absolute_uri(f'{path}?token={token}'),
        'expira_en_segundos': settings.DOCUMENTOS_DOWNLOAD_TOKEN_SECONDS,
    })


@api_view(['GET'])
def documento_descarga(request, id_documento):
    token = request.GET.get('token')
    if not token:
        raise ValueError('Token de descarga requerido')

    try:
        payload = signing.loads(
            token,
            salt='documento-download',
            max_age=settings.DOCUMENTOS_DOWNLOAD_TOKEN_SECONDS,
        )
    except signing.BadSignature as exc:
        raise ValueError('Token de descarga inválido o expirado') from exc

    if int(payload.get('id_documento')) != int(id_documento):
        raise ValueError('Token de descarga no corresponde al documento solicitado')

    user = payload.get('user') or {}
    documento = call_service('DOCUM', 'obtener_archivo_descarga', {'id_documento': id_documento}, user)
    absolute_path = document_absolute_path(documento['ruta_relativa'])
    if not absolute_path.exists():
        raise Http404('Archivo no encontrado')

    call_service('DOCUM', 'registrar_descarga', {
        'id_documento': id_documento,
        'ip': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
    }, user)

    return FileResponse(
        absolute_path.open('rb'),
        as_attachment=True,
        filename=documento['nombre_original'],
        content_type='application/pdf',
    )


@api_view(['GET'])
@require_auth
def documentos_auditoria(request):
    filters = {
        'id_documento': request.GET.get('id_documento'),
        'id_usuario': request.GET.get('id_usuario'),
        'accion': request.GET.get('accion'),
    }
    filters = {k: v for k, v in filters.items() if v}
    return ok(call_service('DOCUM', 'auditoria_documento', filters, request.current_user))
