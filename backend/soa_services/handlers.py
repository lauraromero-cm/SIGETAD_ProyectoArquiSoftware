from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError, transaction
from django.db.models import Q
from datetime import datetime

from usuarios.models import Usuario
from vacantes.models import Vacante
from candidatos.models import Candidato
from postulaciones.models import Postulacion
from evaluaciones.models import Evaluacion
from historial.models import Historial
from .serializers import (
    usuario_to_dict,
    vacante_to_dict,
    candidato_to_dict,
    postulacion_to_dict,
    evaluacion_to_dict,
    historial_to_dict,
)
from .permissions import require_roles, require_user


SERVICE_CODES = {
    'USUAR': 'usuarios',
    'VACAN': 'vacantes',
    'CANDI': 'candidatos',
    'POSTU': 'postulaciones',
    'EVALU': 'evaluaciones',
    'HISTO': 'historial',
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
    raise ValueError('Servicio no reconocido')


# ---------------- Usuarios ----------------
def handle_usuarios(action, data, user):
    if action == 'login':
        correo = data.get('correo', '').strip().lower()
        contrasena = data.get('contrasena', '')
        try:
            usuario = Usuario.objects.get(correo=correo, estado=Usuario.ESTADO_ACTIVO)
        except Usuario.DoesNotExist:
            raise ValueError('Credenciales inválidas')
        if not check_password(contrasena, usuario.contrasena):
            raise ValueError('Credenciales inválidas')
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
        return {'usuario': usuario_to_dict(usuario), 'candidato': candidato_to_dict(candidato)}

    if action == 'crear_usuario':
        require_roles(user, ['admin'])
        nombre = data.get('nombre', '')
        correo = data.get('correo', '').strip().lower()
        rol = data.get('rol', '')
        contrasena = data.get('contrasena') or 'admin123'
        if rol not in dict(Usuario.ROLES):
            raise ValueError('Rol inválido')
        usuario = Usuario.objects.create(
            nombre=nombre,
            correo=correo,
            contrasena=make_password(contrasena),
            rol=rol,
            estado=data.get('estado') or Usuario.ESTADO_ACTIVO,
        )
        return usuario_to_dict(usuario)

    if action == 'listar_usuarios':
        require_roles(user, ['admin'])
        return [usuario_to_dict(u) for u in Usuario.objects.all()]

    if action == 'cambiar_estado':
        require_roles(user, ['admin'])
        usuario = Usuario.objects.get(id_usuario=data.get('id_usuario'))
        usuario.estado = data.get('estado')
        usuario.save(update_fields=['estado'])
        return usuario_to_dict(usuario)

    if action == 'eliminar_usuario':
        require_roles(user, ['admin'])
        usuario = Usuario.objects.get(id_usuario=data.get('id_usuario'))
        usuario_dict = usuario_to_dict(usuario)
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
        return vacante_to_dict(v)

    if action == 'editar_vacante':
        require_roles(user, ['admin', 'analista'])
        v = Vacante.objects.get(id_vacante=data.get('id_vacante'))
        for field in ['titulo', 'descripcion', 'departamento', 'salario_minimo', 'salario_maximo', 'requisitos', 'estado']:
            if field in data:
                setattr(v, field, data[field])
        v.save()
        return vacante_to_dict(v)

    if action == 'cerrar_vacante':
        require_roles(user, ['admin', 'analista'])
        v = Vacante.objects.get(id_vacante=data.get('id_vacante'))
        v.estado = Vacante.ESTADO_CERRADA
        v.save(update_fields=['estado'])
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
        for field in ['nombre_completo', 'email', 'telefono', 'profesion', 'experiencia_anios', 'cv', 'foto_perfil']:
            if field in data:
                setattr(candidato, field, data[field] or (0 if field == 'experiencia_anios' else ''))
        candidato.save()
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
        estado = data.get('estado')
        if estado not in dict(Postulacion.ESTADOS):
            raise ValueError('Estado de postulación inválido')
        with transaction.atomic():
            p.estado = estado
            p.notas = data.get('notas', p.notas)
            p.save(update_fields=['estado', 'notas'])
            Historial.objects.create(
                id_postulacion=p,
                tipo='estado',
                descripcion=f'Estado actualizado a {estado}',
                id_usuario_id=user['id_usuario'],
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
        require_user(user)
        qs = Historial.objects.select_related('id_usuario', 'id_postulacion')
        
        # Filtro por postulación
        if data.get('id_postulacion'):
            qs = qs.filter(id_postulacion_id=data['id_postulacion'])
        
        # Filtro por tipo de evento
        if data.get('tipo'):
            qs = qs.filter(tipo=data['tipo'])
        
        # Filtro por usuario que realizó la acción
        if data.get('id_usuario'):
            qs = qs.filter(id_usuario_id=data['id_usuario'])
        
        # Filtro por rango de fechas
        if data.get('fecha_desde'):
            fecha_desde = datetime.fromisoformat(data['fecha_desde']).date() if isinstance(data['fecha_desde'], str) else data['fecha_desde']
            qs = qs.filter(fecha__date__gte=fecha_desde)
        
        if data.get('fecha_hasta'):
            fecha_hasta = datetime.fromisoformat(data['fecha_hasta']).date() if isinstance(data['fecha_hasta'], str) else data['fecha_hasta']
            qs = qs.filter(fecha__date__lte=fecha_hasta)
        
        # Búsqueda de texto en descripción
        if data.get('q'):
            qs = qs.filter(descripcion__icontains=data['q'])
        
        # Ordenamiento (por defecto más reciente primero)
        orden = data.get('orden', '-fecha')
        qs = qs.order_by(orden)
        
        return [historial_to_dict(h) for h in qs]

    if action == 'registrar_evento':
        require_roles(user, ['admin', 'analista', 'jefe_area'])
        h = Historial.objects.create(
            id_postulacion_id=data.get('id_postulacion'),
            tipo=data.get('tipo', 'evento'),
            descripcion=data.get('descripcion', ''),
            id_usuario_id=user['id_usuario'],
        )
        return historial_to_dict(h)

    raise ValueError('Operación de historial no reconocida')
