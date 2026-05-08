def require_user(user):
    if not user or not user.get('id_usuario'):
        raise PermissionError('Autenticación requerida')


def require_roles(user, allowed):
    require_user(user)
    if user.get('rol') not in allowed:
        raise PermissionError('No tienes permisos para realizar esta acción')
