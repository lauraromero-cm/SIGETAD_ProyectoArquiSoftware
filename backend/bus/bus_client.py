import json
import os
from django.conf import settings
from .soa_lib import connect_to_bus, send_message, receive_message, split_message


class BusClientError(Exception):
    pass


def call_service(service_code: str, action: str, data=None, user=None):
    payload = {
        'action': action,
        'data': data or {},
        'user': user or {},
    }
    host = getattr(settings, 'BUS_HOST', os.getenv('BUS_HOST', 'localhost'))
    port = int(getattr(settings, 'BUS_PORT', os.getenv('BUS_PORT', '5000')))

    try:
        sock = connect_to_bus(host, port, timeout=15)
        try:
            send_message(sock, service_code, json.dumps(payload, ensure_ascii=False))
            raw = receive_message(sock)
            if raw is None:
                raise BusClientError('El bus no devolvió respuesta')
            response_service, response_payload = split_message(raw)
            if response_service != service_code:
                raise BusClientError(f'Respuesta inesperada del servicio {response_service}')
            response = json.loads(response_payload)
            if not response.get('ok', False):
                raise BusClientError(response.get('error', 'Error desconocido'))
            return response.get('data')
        finally:
            sock.close()
    except BusClientError:
        raise
    except Exception as exc:
        raise BusClientError(f'No se pudo comunicar con el bus/servicio {service_code}: {exc}') from exc
