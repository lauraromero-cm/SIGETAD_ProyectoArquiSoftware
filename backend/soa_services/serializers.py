from decimal import Decimal
from django.utils import timezone


def iso(dt):
    return dt.isoformat() if dt else None


def money(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def usuario_to_dict(u):
    return {
        'id_usuario': u.id_usuario,
        'nombre': u.nombre,
        'correo': u.correo,
        'rol': u.rol,
        'estado': u.estado,
    }


def vacante_to_dict(v):
    return {
        'id_vacante': v.id_vacante,
        'titulo': v.titulo,
        'descripcion': v.descripcion,
        'departamento': v.departamento,
        'salario_minimo': money(v.salario_minimo),
        'salario_maximo': money(v.salario_maximo),
        'requisitos': v.requisitos,
        'estado': v.estado,
        'creado_por': v.creado_por_id,
        'creado_por_nombre': getattr(v.creado_por, 'nombre', None),
    }


def candidato_to_dict(c):
    return {
        'id_candidato': c.id_candidato,
        'id_usuario': c.id_usuario_id,
        'nombre_completo': c.nombre_completo,
        'email': c.email,
        'telefono': c.telefono,
        'profesion': c.profesion,
        'experiencia_anios': c.experiencia_anios,
        'cv': c.cv,
        'foto_perfil': c.foto_perfil,
    }


def postulacion_to_dict(p):
    candidato = getattr(p, 'id_candidato', None)
    vacante = getattr(p, 'id_vacante', None)
    return {
        'id_postulacion': p.id_postulacion,
        'id_candidato': p.id_candidato_id,
        'id_vacante': p.id_vacante_id,
        'estado': p.estado,
        'fecha_postulacion': iso(p.fecha_postulacion),
        'notas': p.notas,
        'candidato_nombre': getattr(candidato, 'nombre_completo', None),
        'candidato_email': getattr(candidato, 'email', None),
        'vacante_titulo': getattr(vacante, 'titulo', None),
        'vacante_departamento': getattr(vacante, 'departamento', None),
    }


def evaluacion_to_dict(e):
    return {
        'id_evaluacion': e.id_evaluacion,
        'id_postulacion': e.id_postulacion_id,
        'id_usuario': e.id_usuario_id,
        'evaluador_nombre': getattr(e.id_usuario, 'nombre', None),
        'calificacion': e.calificacion,
        'comentarios': e.comentarios,
    }


def historial_to_dict(h):
    return {
        'id_historial': h.id_historial,
        'id_postulacion': h.id_postulacion_id,
        'tipo': h.tipo,
        'descripcion': h.descripcion,
        'id_usuario': h.id_usuario_id,
        'usuario_nombre': getattr(h.id_usuario, 'nombre', None),
        'fecha': iso(h.fecha),
        # Campos nuevos para auditoría mejorada
        'cambios_detalles': h.cambios_detalles or {},
        'is_deleted': h.is_deleted,
        'fecha_eliminacion': iso(h.fecha_eliminacion),
        'id_entidad_tipo': h.id_entidad_tipo,
        'id_entidad_referencia': h.id_entidad_referencia,
    }


def documento_to_dict(d):
    usuario = getattr(d, 'id_usuario', None)
    postulacion = getattr(d, 'id_postulacion', None)
    return {
        'id_documento': d.id_documento,
        'nombre_original': d.nombre_original,
        'content_type': d.content_type,
        'tamanio_bytes': d.tamanio_bytes,
        'checksum_sha256': d.checksum_sha256,
        'estado': d.estado,
        'id_usuario': d.id_usuario_id,
        'usuario_nombre': getattr(usuario, 'nombre', None),
        'id_postulacion': d.id_postulacion_id,
        'fecha_subida': iso(d.fecha_subida),
        'candidato_nombre': getattr(getattr(postulacion, 'id_candidato', None), 'nombre_completo', None),
        'vacante_titulo': getattr(getattr(postulacion, 'id_vacante', None), 'titulo', None),
    }


def documento_auditoria_to_dict(a):
    return {
        'id_auditoria': a.id_auditoria,
        'id_documento': a.id_documento_id,
        'id_usuario': a.id_usuario_id,
        'usuario_nombre': getattr(a.id_usuario, 'nombre', None),
        'accion': a.accion,
        'fecha': iso(a.fecha),
        'detalles': a.detalles or {},
    }
