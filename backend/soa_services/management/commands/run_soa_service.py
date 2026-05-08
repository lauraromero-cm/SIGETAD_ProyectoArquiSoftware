import json
import os
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from bus.soa_lib import connect_to_bus, send_message, receive_message, split_message
from soa_services.handlers import SERVICE_CODES, handle


class Command(BaseCommand):
    help = 'Levanta un servicio SOA conectado al bus TCP/ESB.'

    def add_arguments(self, parser):
        parser.add_argument('service_code', type=str, help='Código de servicio de 5 caracteres: USUAR, VACAN, CANDI, POSTU, EVALU, HISTO')

    def handle(self, *args, **options):
        service_code = options['service_code'].upper()
        if service_code not in SERVICE_CODES:
            raise CommandError(f'Servicio inválido: {service_code}')

        host = getattr(settings, 'BUS_HOST', os.getenv('BUS_HOST', 'localhost'))
        port = int(getattr(settings, 'BUS_PORT', os.getenv('BUS_PORT', '5000')))
        self.stdout.write(self.style.SUCCESS(f'Iniciando servicio {service_code} ({SERVICE_CODES[service_code]})'))

        while True:
            sock = None
            try:
                sock = connect_to_bus(host, port)
                send_message(sock, 'sinit', service_code)
                confirmation = receive_message(sock)
                self.stdout.write(f'Confirmación del bus: {confirmation!r}')

                while True:
                    raw = receive_message(sock)
                    if raw is None:
                        raise RuntimeError('Conexión cerrada por el bus')
                    received_service, payload = split_message(raw)
                    if received_service != service_code:
                        raise RuntimeError(f'Mensaje recibido para servicio incorrecto: {received_service}')

                    try:
                        request = json.loads(payload)
                        action = request.get('action')
                        data = request.get('data') or {}
                        user = request.get('user') or {}
                        result = handle(service_code, action, data, user)
                        response = {'ok': True, 'error': None, 'data': result}
                    except Exception as exc:
                        response = {'ok': False, 'error': str(exc), 'data': None}

                    send_message(sock, service_code, json.dumps(response, ensure_ascii=False, default=str))
            except Exception as exc:
                self.stderr.write(f'Error en servicio {service_code}: {exc}. Reintentando en 3s...')
                try:
                    if sock:
                        sock.close()
                except OSError:
                    pass
                time.sleep(3)
