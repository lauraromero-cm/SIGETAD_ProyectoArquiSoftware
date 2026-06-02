from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from datetime import timedelta

from usuarios.models import LoginIntento, Usuario
from vacantes.models import Vacante
from candidatos.models import Candidato
from postulaciones.models import Postulacion
from evaluaciones.models import Evaluacion
from historial.models import Historial
from documentos.models import Documento, DocumentoAuditoria
from .serializers import (
    usuario_to_dict,
    vacante_to_dict,
    candidato_to_dict,
    postulacion_to_dict,
    evaluacion_to_dict,
    historial_to_dict,
    documento_to_dict,
    documento_auditoria_to_dict,
)
from .permissions import require_roles, require_user


SERVICE_CODES = {
    'USUAR': 'usuarios',
    'VACAN': 'vacantes',
    'CANDI': 'candidatos',
    'POSTU': 'postulaciones',
    'EVALU': 'evaluaciones',
    'HISTO': 'historial',
    'DOCUM': 'documentos',
}


def handle(service_code, action, data, user):
    if service_code == 'USUAR':
        return handle_usuarios(action, data, user)
    if service_code == 'VACAN':
        return handle_vacantes(action, data, user)
    if service_code == 'CANDI':
        return handle_candidatos(action, data, user)
    if service_code == 'POSTU':
        return handle_postulaciones(action, data, user)
    if service_code == 'EVALU':
        return handle_evaluaciones(action, data, user)
    if service_code == 'HISTO':
        return handle_historial(action, data, user)
    if service_code == 'DOCUM':
        return handle_documentos(action, data, user)
    raise ValueError('Servicio no reconocido')


def _registrar_historial(user_id, descripcion, entidad_tipo=Historial.ENTIDAD_USUARIO, entidad_id=None, tipo=Historial.TIPO_EVENTO, cambios=None, id_postulacion=None):
    if not user_id:
        return None
    return Historial.objects.create(
        id_postulacion_id=id_postulacion,
        tipo=tipo,
        descripcion=descripcion,
        id_usuario_id=user_id,
        cambios_detalles=cambios or {},
        id_entidad_tipo=entidad_tipo,
        id_entidad_referencia=entidad_id,
    )


def _audit_changes(before, after, fields):
    changes = {}
    for field in fields:
        old = before.get(field)
        new = after.get(field)
        if old != new:
            changes[field] = {'valor_anterior': old, 'valor_nuevo': new}
    return changes


# ---------------- Usuarios ----------------
def handle_usuarios(action, data, user):
    if action == 'login':
        correo = data.get('correo', '').strip().lower()
        contrasena = data.get('contrasena', '')
        ip = data.get('ip') or None
        user_agent = (data.get('user_agent') or '')[:255]
        desde = timezone.now() - timedelta(seconds=settings.LOGIN_LOCKOUT_SECONDS)
        fallidos = LoginIntento.objects.filter(correo=correo, resultado=LoginIntento.RESULTADO_FALLIDO, fecha__gte=desde).count()
        if fallidos >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
            LoginIntento.objects.create(correo=correo, resultado=LoginIntento.RESULTADO_BLOQUEADO, ip=ip, user_agent=user_agent)
            raise ValueError('Cuenta temporalmente bloqueada por múltiples intentos fallidos')
        try:
            usuario = Usuario.objects.get(correo=correo, estado=Usuario.ESTADO_ACTIVO)
        except Usuario.DoesNotExist:
            LoginIntento.objects.create(correo=correo, resultado=LoginIntento.RESULTADO_FALLIDO, ip=ip, user_agent=user_agent)
            raise ValueError('Credenciales inválidas')
        if not check_password(contrasena, usuario.contrasena):
            LoginIntento.objects.create(correo=correo, resultado=LoginIntento.RESULTADO_FALLIDO, ip=ip, user_agent=user_agent, id_usuario=usuario)
            raise ValueError('Credenciales inválidas')
        LoginIntento.objects.create(correo=correo, resultado=LoginIntento.RESULTADO_EXITO, ip=ip, user_agent=user_agent, id_usuario=usuario)
        _registrar_historial(usuario.id_usuario, 'Inicio de sesión exitoso', Historial.ENTIDAD_USUARIO, usuario.id_usuario)
        return usuario_to_dict(usuario)

    if action == 'registrar_candidato_usuario':
        nombre = data.get('nombre') or data.get('nombre_completo') or ''
        correo = (data.get('correo') or data.get('email') or '').strip().lower()
        contrasena = data.get('contrasena') or 'admin123'
        if not nombre or not correo:
            raise ValueError('Nombre y correo son obligatorios')
        with transaction.atomic():
            usuario = Usuario.objects.create(
                nombre=nombre,
                correo=correo,
                contrasena=make_password(contrasena),
                rol=Usuario.ROL_CANDIDATO,
            )
            candidato = Candidato.objects.create(
                id_usuario=usuario,
                nombre_completo=nombre,
                email=correo,
                telefono=data.get('telefono', ''),
                profesion=data.get('profesion', ''),
                experiencia_anios=int(data.get('experiencia_anios') or 0),
                cv=data.get('cv', ''),
                foto_perfil=data.get('foto_perfil', ''),
            )
            _registrar_historial(usuario.id_usuario, 'Registro de candidato', Historial.ENTIDAD_CANDIDATO, candidato.id_candidato)
        return {'usuario': usuario_to_dict(usuario), 'candidato': candidato_to_dict(candidato)}

    if action == 'crear_usuario':
        require_roles(user, ['admin'])
        nombre = data.get('nombre', '')
        correo = data.get('correo', '').strip().lower()
        rol = data.get('rol', '')
        contrasena = data.get('contrasena') or 'admin123'
        if rol not in dict(Usuario.ROLES):
            raise ValueError('Rol inválido')
        with transaction.atomic():
            usuario = Usuario.objects.create(
                nombre=nombre,
                correo=correo,
                contrasena=make_password(contrasena),
                rol=rol,
                estado=data.get('estado') or Usuario.ESTADO_ACTIVO,
            )
            _registrar_historial(user['id_usuario'], f'Usuario creado: {usuario.correo}', Historial.ENTIDAD_USUARIO, usuario.id_usuario)
        return usuario_to_dict(usuario)

    if action == 'listar_usuarios':
        require_roles(user, ['admin'])
        return [usuario_to_dict(u) for u in Usuario.objects.all()]

    if action == 'cambiar_estado':
        require_roles(user, ['admin'])
        usuario = Usuario.objects.get(id_usuario=data.get('id_usuario'))
        estado_anterior = usuario.estado
        usuario.estado = data.get('estado')
        usuario.save(update_fields=['estado'])
        _registrar_historial(
            user['id_usuario'],
            f'Estado de usuario {usuario.correo} cambió de "{estado_anterior}" a "{usuario.estado}"',
            Historial.ENTIDAD_USUARIO,
            usuario.id_usuario,
            Historial.TIPO_CAMBIO_CAMPO,
            {'campo': 'estado', 'valor_anterior': estado_anterior, 'valor_nuevo': usuario.estado},
        )
        return usuario_to_dict(usuario)

    if action == 'eliminar_usuario':
        require_roles(user, ['admin'])
        usuario = Usuario.objects.get(id_usuario=data.get('id_usuario'))
        usuario_dict = usuario_to_dict(usuario)
        _registrar_historial(user['id_usuario'], f'Usuario eliminado: {usuario.correo}', Historial.ENTIDAD_USUARIO, usuario.id_usuario)
        usuario.delete()
        return {'mensaje': 'Usuario eliminado correctamente', 'usuario': usuario_dict}

    raise ValueError('Operación de usuarios no reconocida')


# ---------------- Vacantes ----------------
def handle_vacantes(action, data, user):
    if action == 'listar_vacantes':
        qs = Vacante.objects.select_related('creado_por')
        if data.get('solo_abiertas', True):
            qs = qs.filter(estado=Vacante.ESTADO_ABIERTA)
        return [vacante_to_dict(v) for v in qs]

    if action == 'obtener_vacante':
        v = Vacante.objects.select_related('creado_por').get(id_vacante=data.get('id_vacante'))
        return vacante_to_dict(v)

    if action == 'crear_vacante':
        require_roles(user, ['admin', 'analista'])
        creador = Usuario.objects.get(id_usuario=user['id_usuario'])
        with transaction.atomic():
            v = Vacante.objects.create(
                titulo=data.get('titulo', ''),
                descripcion=data.get('descripcion', ''),
                departamento=data.get('departamento', ''),
                salario_minimo=data.get('salario_minimo') or 0,
                salario_maximo=data.get('salario_maximo') or 0,
                requisitos=data.get('requisitos', ''),
                estado=data.get('estado') or Vacante.ESTADO_ABIERTA,
                creado_por=creador,
            )
            _registrar_historial(user['id_usuario'], f'Vacante creada: {v.titulo}', Historial.ENTIDAD_VACANTE, v.id_vacante)
        return vacante_to_dict(v)

    if action == 'editar_vacante':
        require_roles(user, ['admin', 'analista'])
        v = Vacante.objects.get(id_vacante=data.get('id_vacante'))
        fields = ['titulo', 'descripcion', 'departamento', 'salario_minimo', 'salario_maximo', 'requisitos', 'estado']
        before = {field: getattr(v, field) for field in fields}
        for field in ['titulo', 'descripcion', 'departamento', 'salario_minimo', 'salario_maximo', 'requisitos', 'estado']:
            if field in data:
                setattr(v, field, data[field])
        v.save()
        after = {field: getattr(v, field) for field in fields}
        cambios = _audit_changes(before, after, fields)
        if cambios:
            _registrar_historial(
                user['id_usuario'],
                f'Vacante editada: {v.titulo}',
                Historial.ENTIDAD_VACANTE,
                v.id_vacante,
                Historial.TIPO_CAMBIO_CAMPO,
                cambios,
            )
        return vacante_to_dict(v)

    if action == 'cerrar_vacante':
        require_roles(user, ['admin', 'analista'])
        v = Vacante.objects.get(id_vacante=data.get('id_vacante'))
        estado_anterior = v.estado
        v.estado = Vacante.ESTADO_CERRADA
        v.save(update_fields=['estado'])
        _registrar_historial(
            user['id_usuario'],
            f'Vacante cerrada: {v.titulo}',
            Historial.ENTIDAD_VACANTE,
            v.id_vacante,
            Historial.TIPO_CAMBIO_CAMPO,
            {'campo': 'estado', 'valor_anterior': estado_anterior, 'valor_nuevo': v.estado},
        )
        return vacante_to_dict(v)

    raise ValueError('Operación de vacantes no reconocida')


# ---------------- Candidatos ----------------
def handle_candidatos(action, data, user):
    if action == 'mi_perfil':
        require_roles(user, ['candidato'])
        c = Candidato.objects.get(id_usuario_id=user['id_usuario'])
        return candidato_to_dict(c)

    if action == 'guardar_perfil':
        require_roles(user, ['candidato'])
        usuario = Usuario.objects.get(id_usuario=user['id_usuario'])
        candidato, _ = Candidato.objects.get_or_create(
            id_usuario=usuario,
            defaults={
                'nombre_completo': data.get('nombre_completo') or usuario.nombre,
                'email': data.get('email') or usuario.correo,
            },
        )
        fields = ['nombre_completo', 'email', 'telefono', 'profesion', 'experiencia_anios', 'cv', 'foto_perfil']
        before = {field: getattr(candidato, field) for field in fields}
        for field in ['nombre_completo', 'email', 'telefono', 'profesion', 'experiencia_anios', 'cv', 'foto_perfil']:
            if field in data:
                value = data[field]
                if field == 'experiencia_anios':
                    value = int(str(value or 0).replace('+', '') or 0)
                setattr(candidato, field, value or (0 if field == 'experiencia_anios' else ''))
        candidato.save()
        after = {field: getattr(candidato, field) for field in fields}
        cambios = _audit_changes(before, after, fields)
        if cambios:
            _registrar_historial(
                user['id_usuario'],
                'Perfil de candidato actualizado',
                Historial.ENTIDAD_CANDIDATO,
                candidato.id_candidato,
                Historial.TIPO_CAMBIO_CAMPO,
                cambios,
            )
        return candidato_to_dict(candidato)

    if action == 'listar_candidatos':
        require_roles(user, ['admin', 'analista', 'jefe_area'])
        qs = Candidato.objects.all()
        texto = data.get('q')
        if texto:
            qs = qs.filter(Q(nombre_completo__icontains=texto) | Q(email__icontains=texto) | Q(profesion__icontains=texto))
        return [candidato_to_dict(c) for c in qs]

    if action == 'obtener_candidato':
        require_roles(user, ['admin', 'analista', 'jefe_area'])
        c = Candidato.objects.get(id_candidato=data.get('id_candidato'))
        return candidato_to_dict(c)

    if action == 'obtener_archivo_perfil':
        require_user(user)
        candidato = Candidato.objects.get(id_candidato=data.get('id_candidato'))
        if user.get('rol') == 'candidato' and candidato.id_usuario_id != user['id_usuario']:
            raise PermissionError('No tienes permisos para ver este archivo')
        if user.get('rol') != 'candidato':
            require_roles(user, ['admin', 'analista', 'jefe_area'])

        tipo = data.get('tipo')
        if tipo == 'cv':
            ruta = candidato.cv
        elif tipo == 'foto':
            ruta = candidato.foto_perfil
        else:
            raise ValueError('Tipo de archivo inválido')
        if not ruta:
            raise ValueError('El candidato no tiene archivo cargado')
        return {
            'id_candidato': candidato.id_candidato,
            'tipo': tipo,
            'ruta_relativa': ruta,
            'nombre_candidato': candidato.nombre_completo,
        }

    if action == 'registrar_acceso_archivo_perfil':
        require_user(user)
        candidato = Candidato.objects.get(id_candidato=data.get('id_candidato'))
        if user.get('rol') == 'candidato' and candidato.id_usuario_id != user['id_usuario']:
            raise PermissionError('No tienes permisos para auditar este archivo')
        if user.get('rol') != 'candidato':
            require_roles(user, ['admin', 'analista', 'jefe_area'])
        tipo = data.get('tipo')
        accion = data.get('accion', 'visualización')
        _registrar_historial(
            user['id_usuario'],
            f'{accion.capitalize()} de archivo {tipo} del candidato {candidato.nombre_completo}',
            Historial.ENTIDAD_CANDIDATO,
            candidato.id_candidato,
            Historial.TIPO_EVENTO,
            {'archivo_tipo': tipo, 'accion': accion},
        )
        return {'mensaje': 'Acceso auditado'}

    raise ValueError('Operación de candidatos no reconocida')


# ---------------- Postulaciones ----------------
def handle_postulaciones(action, data, user):
    if action == 'postular':
        require_roles(user, ['candidato'])
        candidato = Candidato.objects.get(id_usuario_id=user['id_usuario'])
        vacante = Vacante.objects.get(id_vacante=data.get('id_vacante'), estado=Vacante.ESTADO_ABIERTA)
        
        # Validar que el candidato no esté ya postulado a esta vacante
        existe = Postulacion.objects.filter(id_candidato=candidato, id_vacante=vacante).exists()
        if existe:
            raise ValueError('Ya has postulado a esta vacante')
        
        with transaction.atomic():
            p = Postulacion.objects.create(
                id_candidato=candidato,
                id_vacante=vacante,
                notas=data.get('notas', ''),
            )
            Historial.objects.create(
                id_postulacion=p,
                tipo='postulacion',
                descripcion=f'Candidato postuló a la vacante {vacante.titulo}',
                id_usuario_id=user['id_usuario'],
            )
        return postulacion_to_dict(p)

    if action == 'listar_postulaciones':
        require_user(user)
        qs = Postulacion.objects.select_related('id_candidato', 'id_vacante')
        if user.get('rol') == 'candidato':
            qs = qs.filter(id_candidato__id_usuario_id=user['id_usuario'])
        if data.get('id_vacante'):
            qs = qs.filter(id_vacante_id=data['id_vacante'])
        if data.get('estado'):
            qs = qs.filter(estado=data['estado'])
        if data.get('q'):
            q = data['q']
            qs = qs.filter(Q(id_candidato__nombre_completo__icontains=q) | Q(id_vacante__titulo__icontains=q) | Q(estado__icontains=q))
        return [postulacion_to_dict(p) for p in qs]

    if action == 'actualizar_estado':
        require_roles(user, ['admin', 'analista'])
        p = Postulacion.objects.select_related('id_vacante', 'id_candidato').get(id_postulacion=data.get('id_postulacion'))
        estado_anterior = p.estado
        estado = data.get('estado')
        if estado not in dict(Postulacion.ESTADOS):
            raise ValueError('Estado de postulación inválido')
        with transaction.atomic():
            p.estado = estado
            p.notas = data.get('notas', p.notas)
            p.save(update_fields=['estado', 'notas'])
            
            # Registro con cambios detalladossistema
            cambios = {
                'campo': 'estado',
                'valor_anterior': estado_anterior,
                'valor_nuevo': estado,
            }
            Historial.objects.create(
                id_postulacion=p,
                tipo=Historial.TIPO_CAMBIO_CAMPO,
                descripcion=f'Estado cambió de "{estado_anterior}" a "{estado}"',
                id_usuario_id=user['id_usuario'],
                cambios_detalles=cambios,
                id_entidad_tipo=Historial.ENTIDAD_POSTULACION,
                id_entidad_referencia=p.id_postulacion,
            )
        return postulacion_to_dict(p)

    if action == 'obtener_postulacion':
        require_user(user)
        p = Postulacion.objects.select_related('id_candidato', 'id_vacante').get(id_postulacion=data.get('id_postulacion'))
        if user.get('rol') == 'candidato' and p.id_candidato.id_usuario_id != user['id_usuario']:
            raise PermissionError('No tienes permisos para ver esta postulación')
        return postulacion_to_dict(p)

    raise ValueError('Operación de postulaciones no reconocida')


# ---------------- Evaluaciones ----------------
def handle_evaluaciones(action, data, user):
    if action == 'registrar_evaluacion':
        require_roles(user, ['admin', 'jefe_area', 'analista'])
        p = Postulacion.objects.get(id_postulacion=data.get('id_postulacion'))
        calificacion = int(data.get('calificacion') or 0)
        if calificacion < 1 or calificacion > 5:
            raise ValueError('La calificación debe estar entre 1 y 5')
        with transaction.atomic():
            e, _ = Evaluacion.objects.update_or_create(
                id_postulacion=p,
                defaults={
                    'id_usuario_id': user['id_usuario'],
                    'calificacion': calificacion,
                    'comentarios': data.get('comentarios', ''),
                },
            )
            Historial.objects.create(
                id_postulacion=p,
                tipo='evaluacion',
                descripcion=f'Evaluación registrada con calificación {calificacion}',
                id_usuario_id=user['id_usuario'],
            )
        return evaluacion_to_dict(e)

    if action == 'listar_evaluaciones':
        require_user(user)
        qs = Evaluacion.objects.select_related('id_usuario')
        
        # Si es candidato, solo mostrar evaluaciones de sus propias postulaciones
        if user.get('rol') == 'candidato':
            candidato = Candidato.objects.get(id_usuario_id=user['id_usuario'])
            qs = qs.filter(id_postulacion__id_candidato=candidato)
        
        if data.get('id_postulacion'):
            qs = qs.filter(id_postulacion_id=data['id_postulacion'])
        return [evaluacion_to_dict(e) for e in qs]

    raise ValueError('Operación de evaluaciones no reconocida')


# ---------------- Historial ----------------
def handle_historial(action, data, user):
    if action == 'listar_historial':
        require_roles(user, ['admin', 'candidato'])
        qs = Historial.objects.select_related(
            'id_usuario',
            'id_postulacion',
            'id_postulacion__id_candidato',
        ).filter(is_deleted=False)

        if user.get('rol') == 'candidato':
            try:
                candidato = Candidato.objects.get(id_usuario_id=user['id_usuario'])
            except Candidato.DoesNotExist:
                return []
            qs = qs.filter(
                Q(id_postulacion__id_candidato=candidato) |
                Q(id_entidad_tipo=Historial.ENTIDAD_CANDIDATO, id_entidad_referencia=candidato.id_candidato)
            )
        
        # Filtro por postulación
        if data.get('id_postulacion'):
            try:
                id_postulacion = int(data['id_postulacion'])
                qs = qs.filter(id_postulacion_id=id_postulacion)
            except (ValueError, TypeError):
                # Si no es un ID válido, continuar sin filtro
                pass
        
        # Filtro por tipo de evento
        if data.get('tipo'):
            qs = qs.filter(tipo=data['tipo'])
        
        # Filtro por usuario que realizó la acción
        if data.get('id_usuario'):
            qs = qs.filter(id_usuario_id=data['id_usuario'])

        if data.get('id_entidad') and data.get('tipo_entidad'):
            qs = qs.filter(id_entidad_referencia=data['id_entidad'], id_entidad_tipo=data['tipo_entidad'])
        
        # Filtro por rango de fechas
        if data.get('fecha_desde'):
            fecha_desde = datetime.fromisoformat(data['fecha_desde']).date() if isinstance(data['fecha_desde'], str) else data['fecha_desde']
            qs = qs.filter(fecha__date__gte=fecha_desde)
        
        if data.get('fecha_hasta'):
            fecha_hasta = datetime.fromisoformat(data['fecha_hasta']).date() if isinstance(data['fecha_hasta'], str) else data['fecha_hasta']
            qs = qs.filter(fecha__date__lte=fecha_hasta)
        
        # Búsqueda de texto - en descripción o en nombre del usuario
        if data.get('q'):
            q_value = data['q']
            # Opción 1: Buscar en descripción
            query_filter = Q(descripcion__icontains=q_value)
            
            # Opción 2: Buscar usuarios con ese nombre
            matching_usuarios = Usuario.objects.filter(nombre__icontains=q_value).values_list('id_usuario', flat=True)
            if matching_usuarios:
                query_filter = query_filter | Q(id_usuario_id__in=matching_usuarios)
            
            qs = qs.filter(query_filter)
        
        # Ordenamiento (por defecto más reciente primero)
        orden = data.get('orden', '-fecha')
        qs = qs.order_by(orden)
        
        return [historial_to_dict(h) for h in qs]

    if action == 'registrar_evento':
        require_roles(user, ['admin', 'analista', 'jefe_area'])
        h = Historial.objects.create(
            id_postulacion_id=data.get('id_postulacion'),
            tipo=data.get('tipo', Historial.TIPO_EVENTO),
            descripcion=data.get('descripcion', ''),
            id_usuario_id=user['id_usuario'],
            id_entidad_tipo=data.get('id_entidad_tipo', Historial.ENTIDAD_POSTULACION),
            id_entidad_referencia=data.get('id_entidad_referencia'),
        )
        return historial_to_dict(h)

    if action == 'auditar_usuario':
        # Listar todos los eventos que hizo un usuario específico
        require_roles(user, ['admin'])
        id_usuario_a_auditar = data.get('id_usuario')
        if not id_usuario_a_auditar:
            raise ValueError('id_usuario es requerido')
        
        qs = Historial.objects.filter(
            id_usuario_id=id_usuario_a_auditar,
            is_deleted=False
        ).select_related('id_usuario', 'id_postulacion').order_by('-fecha')
        
        # Filtros opcionales
        if data.get('fecha_desde'):
            fecha_desde = datetime.fromisoformat(data['fecha_desde']).date() if isinstance(data['fecha_desde'], str) else data['fecha_desde']
            qs = qs.filter(fecha__date__gte=fecha_desde)
        
        if data.get('fecha_hasta'):
            fecha_hasta = datetime.fromisoformat(data['fecha_hasta']).date() if isinstance(data['fecha_hasta'], str) else data['fecha_hasta']
            qs = qs.filter(fecha__date__lte=fecha_hasta)
        
        return [historial_to_dict(h) for h in qs]

    if action == 'auditar_entidad':
        # Listar todos los cambios de una entidad específica (vacante, candidato, etc)
        require_user(user)
        id_entidad = data.get('id_entidad')
        tipo_entidad = data.get('tipo_entidad')
        
        if not id_entidad or not tipo_entidad:
            raise ValueError('id_entidad y tipo_entidad son requeridos')
        
        qs = Historial.objects.filter(
            id_entidad_referencia=id_entidad,
            id_entidad_tipo=tipo_entidad,
            is_deleted=False
        ).select_related('id_usuario').order_by('-fecha')
        
        return [historial_to_dict(h) for h in qs]

    if action == 'registrar_cambio_detallado':
        # Registra un cambio de campo con antes/después
        require_user(user)
        cambios = {
            'campo': data.get('campo'),
            'valor_anterior': data.get('valor_anterior'),
            'valor_nuevo': data.get('valor_nuevo'),
        }
        
        h = Historial.objects.create(
            id_postulacion_id=data.get('id_postulacion'),
            tipo=Historial.TIPO_CAMBIO_CAMPO,
            descripcion=f"Campo '{data.get('campo')}' cambió de '{data.get('valor_anterior')}' a '{data.get('valor_nuevo')}'",
            id_usuario_id=user['id_usuario'],
            cambios_detalles=cambios,
            id_entidad_tipo=data.get('id_entidad_tipo', Historial.ENTIDAD_POSTULACION),
            id_entidad_referencia=data.get('id_entidad_referencia'),
        )
        return historial_to_dict(h)

    if action == 'soft_delete_evento':
        # Marcar un evento como eliminado sin borrar físicamente (auditoría inmutable)
        require_roles(user, ['admin'])
        h = Historial.objects.get(id_historial=data.get('id_historial'))
        h.marcar_eliminado(user['id_usuario'])
        return {'mensaje': 'Evento marcado como eliminado', 'id_historial': h.id_historial}

    if action == 'exportar_historial_csv':
        # Exportar historial en formato CSV
        require_roles(user, ['admin', 'analista'])
        import csv
        from io import StringIO
        
        qs = Historial.objects.filter(is_deleted=False).select_related('id_usuario', 'id_postulacion')
        
        # Aplicar filtros
        if data.get('id_postulacion'):
            qs = qs.filter(id_postulacion_id=data['id_postulacion'])
        
        if data.get('id_usuario'):
            qs = qs.filter(id_usuario_id=data['id_usuario'])
        
        if data.get('tipo'):
            qs = qs.filter(tipo=data['tipo'])
        
        # Generar CSV en memoria
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'ID Historial', 'Fecha', 'Tipo', 'Descripción', 'Usuario', 
            'ID Postulación', 'Entidad Tipo', 'Cambios Detalles'
        ])
        
        for h in qs.order_by('-fecha'):
            writer.writerow([
                h.id_historial,
                h.fecha.isoformat() if h.fecha else '',
                h.tipo,
                h.descripcion,
                h.id_usuario.nombre if h.id_usuario else '',
                h.id_postulacion_id or '',
                h.id_entidad_tipo,
                str(h.cambios_detalles) if h.cambios_detalles else '',
            ])
        
        return {
            'format': 'csv',
            'filename': f'historial_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'data': output.getvalue(),
            'rows_count': qs.count(),
        }

    if action == 'reporte_cambios_entidad':
        # Generar reporte de cambios realizados a una entidad
        require_user(user)
        id_entidad = data.get('id_entidad')
        tipo_entidad = data.get('tipo_entidad')
        
        if not id_entidad or not tipo_entidad:
            raise ValueError('id_entidad y tipo_entidad son requeridos')
        
        cambios = Historial.objects.filter(
            id_entidad_referencia=id_entidad,
            id_entidad_tipo=tipo_entidad,
            tipo=Historial.TIPO_CAMBIO_CAMPO,
            is_deleted=False
        ).select_related('id_usuario').order_by('-fecha')
        
        timeline = []
        for cambio in cambios:
            detalles = cambio.cambios_detalles or {}
            timeline.append({
                'fecha': cambio.fecha.isoformat(),
                'usuario': cambio.id_usuario.nombre,
                'campo': detalles.get('campo'),
                'valor_anterior': detalles.get('valor_anterior'),
                'valor_nuevo': detalles.get('valor_nuevo'),
                'descripcion': cambio.descripcion,
            })
        
        return {
            'id_entidad': id_entidad,
            'tipo_entidad': tipo_entidad,
            'total_cambios': len(timeline),
            'timeline': timeline,
        }

    raise ValueError('Operación de historial no reconocida')


# ---------------- Documentos ----------------
def _documentos_visibles_para_usuario(user):
    require_user(user)
    qs = Documento.objects.select_related(
        'id_usuario',
        'id_postulacion',
        'id_postulacion__id_candidato',
        'id_postulacion__id_vacante',
    ).filter(estado=Documento.ESTADO_DISPONIBLE)
    if user.get('rol') == 'candidato':
        qs = qs.filter(id_usuario_id=user['id_usuario'])
    return qs


def _obtener_documento_autorizado(id_documento, user):
    qs = _documentos_visibles_para_usuario(user)
    return qs.get(id_documento=id_documento)


def handle_documentos(action, data, user):
    if action == 'registrar_documento':
        require_user(user)
        id_postulacion = data.get('id_postulacion')

        if user.get('rol') == 'candidato':
            candidato = Candidato.objects.get(id_usuario_id=user['id_usuario'])
            if id_postulacion:
                Postulacion.objects.get(id_postulacion=id_postulacion, id_candidato=candidato)

        with transaction.atomic():
            documento = Documento.objects.create(
                nombre_original=data.get('nombre_original', ''),
                nombre_almacenado=data.get('nombre_almacenado', ''),
                ruta_relativa=data.get('ruta_relativa', ''),
                content_type=data.get('content_type', 'application/pdf'),
                tamanio_bytes=int(data.get('tamanio_bytes') or 0),
                checksum_sha256=data.get('checksum_sha256', ''),
                id_usuario_id=user['id_usuario'],
                id_postulacion_id=id_postulacion or None,
            )
            DocumentoAuditoria.objects.create(
                id_documento=documento,
                id_usuario_id=user['id_usuario'],
                accion=DocumentoAuditoria.ACCION_SUBIDA,
                detalles={
                    'nombre_original': documento.nombre_original,
                    'tamanio_bytes': documento.tamanio_bytes,
                    'checksum_sha256': documento.checksum_sha256,
                    'id_postulacion': documento.id_postulacion_id,
                },
            )
        return documento_to_dict(documento)

    if action == 'listar_documentos':
        qs = _documentos_visibles_para_usuario(user)
        if data.get('id_postulacion'):
            qs = qs.filter(id_postulacion_id=data['id_postulacion'])
        if data.get('id_usuario'):
            require_roles(user, ['admin', 'analista', 'jefe_area'])
            qs = qs.filter(id_usuario_id=data['id_usuario'])
        if data.get('q'):
            q = data['q']
            qs = qs.filter(Q(nombre_original__icontains=q) | Q(id_usuario__nombre__icontains=q))
        return [documento_to_dict(d) for d in qs]

    if action == 'obtener_documento':
        documento = _obtener_documento_autorizado(data.get('id_documento'), user)
        return documento_to_dict(documento)

    if action == 'obtener_archivo_descarga':
        documento = _obtener_documento_autorizado(data.get('id_documento'), user)
        return {
            **documento_to_dict(documento),
            'ruta_relativa': documento.ruta_relativa,
        }

    if action == 'registrar_url_generada':
        documento = _obtener_documento_autorizado(data.get('id_documento'), user)
        DocumentoAuditoria.objects.create(
            id_documento=documento,
            id_usuario_id=user['id_usuario'],
            accion=DocumentoAuditoria.ACCION_URL_GENERADA,
            detalles={'expira_en_segundos': data.get('expira_en_segundos')},
        )
        return documento_to_dict(documento)

    if action == 'registrar_descarga':
        documento = _obtener_documento_autorizado(data.get('id_documento'), user)
        DocumentoAuditoria.objects.create(
            id_documento=documento,
            id_usuario_id=user['id_usuario'],
            accion=DocumentoAuditoria.ACCION_DESCARGA,
            detalles={'ip': data.get('ip'), 'user_agent': data.get('user_agent')},
        )
        return {'mensaje': 'Descarga auditada', 'id_documento': documento.id_documento}

    if action == 'auditoria_documento':
        require_roles(user, ['admin', 'analista', 'jefe_area'])
        qs = DocumentoAuditoria.objects.select_related('id_usuario', 'id_documento')
        if data.get('id_documento'):
            qs = qs.filter(id_documento_id=data['id_documento'])
        if data.get('id_usuario'):
            qs = qs.filter(id_usuario_id=data['id_usuario'])
        if data.get('accion'):
            qs = qs.filter(accion=data['accion'])
        return [documento_auditoria_to_dict(a) for a in qs]

    raise ValueError('Operación de documentos no reconocida')
