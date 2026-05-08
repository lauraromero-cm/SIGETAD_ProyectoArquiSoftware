from django.conf import settings
from django.core import signing


TOKEN_SALT = 'sigetad-auth-token'


def make_token(user_data):
    payload = {
        'id_usuario': user_data['id_usuario'],
        'nombre': user_data['nombre'],
        'correo': user_data['correo'],
        'rol': user_data['rol'],
        'estado': user_data['estado'],
    }
    return signing.dumps(payload, salt=TOKEN_SALT)


def verify_token(token):
    return signing.loads(token, salt=TOKEN_SALT, max_age=settings.TOKEN_MAX_AGE_SECONDS)


def get_user_from_request(request):
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        return None
    token = header.split(' ', 1)[1].strip()
    try:
        return verify_token(token)
    except Exception:
        return None
