"""
Bus de Servicios / ESB.

Basado en el protocolo de bus.zip:
- Los servicios se registran con servicio "sinit" y payload = código del servicio.
- Los clientes envían [servicio][payload JSON].
- El bus enruta la solicitud al servicio registrado y retorna la respuesta al cliente.
"""
import os
import socket
import threading
import time
from dataclasses import dataclass
from typing import Dict

from .soa_lib import receive_message, send_message, split_message


@dataclass
class ServiceConnection:
    sock: socket.socket
    lock: threading.Lock


SERVICES: Dict[str, ServiceConnection] = {}
SERVICES_LOCK = threading.Lock()


def register_service(service_code: str, sock: socket.socket):
    if len(service_code) != 5:
        send_message(sock, 'sinit', f'ERROR: código inválido {service_code}')
        sock.close()
        return
    with SERVICES_LOCK:
        old = SERVICES.get(service_code)
        if old:
            try:
                old.sock.close()
            except OSError:
                pass
        SERVICES[service_code] = ServiceConnection(sock=sock, lock=threading.Lock())
    send_message(sock, 'sinit', f'OK registrado {service_code}')
    print(f'[BUS] Servicio registrado: {service_code}', flush=True)


def route_to_service(service_code: str, payload: str, client_sock: socket.socket):
    with SERVICES_LOCK:
        service = SERVICES.get(service_code)
    if not service:
        send_message(client_sock, service_code, '{"ok": false, "error": "Servicio no disponible en el bus", "data": null}')
        return

    with service.lock:
        try:
            send_message(service.sock, service_code, payload)
            response = receive_message(service.sock)
            if response is None:
                raise RuntimeError('Servicio cerró la conexión')
            response_service, response_payload = split_message(response)
            send_message(client_sock, response_service, response_payload)
        except Exception as exc:
            with SERVICES_LOCK:
                SERVICES.pop(service_code, None)
            try:
                service.sock.close()
            except OSError:
                pass
            msg = str(exc).replace('"', '\\"')
            send_message(client_sock, service_code, f'{{"ok": false, "error": "Error comunicando con servicio: {msg}", "data": null}}')


def handle_connection(sock: socket.socket, address):
    try:
        raw = receive_message(sock)
        if raw is None:
            sock.close()
            return
        service_code, payload = split_message(raw)
        if service_code == 'sinit':
            register_service(payload.strip(), sock)
            # El socket queda vivo en SERVICES para uso futuro.
            return
        route_to_service(service_code, payload, sock)
    except Exception as exc:
        print(f'[BUS] Error con {address}: {exc}', flush=True)
    finally:
        # No cerrar sockets de servicios registrados.
        try:
            with SERVICES_LOCK:
                if not any(conn.sock is sock for conn in SERVICES.values()):
                    sock.close()
        except OSError:
            pass


def monitor_services():
    while True:
        time.sleep(10)
        with SERVICES_LOCK:
            registered = ', '.join(sorted(SERVICES.keys())) or 'ninguno'
        print(f'[BUS] Servicios registrados: {registered}', flush=True)


def main():
    host = os.getenv('BUS_HOST', '0.0.0.0')
    port = int(os.getenv('BUS_PORT', '5000'))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(100)
    print(f'[BUS] ESB escuchando en {host}:{port}', flush=True)
    threading.Thread(target=monitor_services, daemon=True).start()
    while True:
        client, address = server.accept()
        threading.Thread(target=handle_connection, args=(client, address), daemon=True).start()


if __name__ == '__main__':
    main()
