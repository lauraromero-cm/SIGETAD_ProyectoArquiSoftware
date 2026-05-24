from django.http import JsonResponse
from bus.bus_client import call_service
from .auth import make_token
from .utils import api_view, parse_json, ok, require_auth


@api_view(['GET'])
def health(request):
    return ok({'status': 'ok', 'app': 'FirmaFast - SIGETAD'})


@api_view(['POST'])
def login(request):
    data = parse_json(request)
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


@api_view(['GET', 'POST'])
@require_auth
def candidato_me(request):
    if request.method == 'GET':
        return ok(call_service('CANDI', 'mi_perfil', user=request.current_user))
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
        return ok(call_service('HISTO', 'listar_historial', {'id_postulacion': request.GET.get('id_postulacion')}, request.current_user))
    return ok(call_service('HISTO', 'registrar_evento', parse_json(request), request.current_user), status=201)
