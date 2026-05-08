import json
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from bus.bus_client import BusClientError
from .auth import get_user_from_request


def parse_json(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError('JSON inválido')


def ok(data=None, status=200):
    return JsonResponse({'ok': True, 'data': data, 'error': None}, status=status, json_dumps_params={'ensure_ascii': False})


def fail(message, status=400):
    return JsonResponse({'ok': False, 'data': None, 'error': str(message)}, status=status, json_dumps_params={'ensure_ascii': False})


def api_view(methods):
    def decorator(fn):
        @csrf_exempt
        @require_http_methods(methods)
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            try:
                return fn(request, *args, **kwargs)
            except BusClientError as exc:
                return fail(exc, 400)
            except ValueError as exc:
                return fail(exc, 400)
            except Exception as exc:
                return fail(exc, 500)
        return wrapper
    return decorator


def require_auth(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        user = get_user_from_request(request)
        if not user:
            return fail('Autenticación requerida', 401)
        request.current_user = user
        return fn(request, *args, **kwargs)
    return wrapper
