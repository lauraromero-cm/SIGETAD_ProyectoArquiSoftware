"""
Librería TCP adaptada desde bus.zip.

Formato original conservado:
[5 bytes largo][5 bytes servicio][payload]

El nombre de servicio debe tener exactamente 5 caracteres.
"""
import socket
from typing import Optional, Tuple

HEADER_SIZE = 5
SERVICE_SIZE = 5


def connect_to_bus(host='localhost', port=5000, timeout: Optional[float] = None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if timeout is not None:
        sock.settimeout(timeout)
    sock.connect((host, int(port)))
    return sock


def send_message(sock: socket.socket, service_name: str, payload: str | bytes):
    if len(service_name) != SERVICE_SIZE:
        raise ValueError('service_name debe tener exactamente 5 caracteres')
    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    content = service_name.encode('utf-8') + payload
    length = str(len(content)).zfill(HEADER_SIZE).encode('utf-8')
    sock.sendall(length + content)


def _recv_exact(sock: socket.socket, amount: int) -> bytes:
    data = b''
    while len(data) < amount:
        chunk = sock.recv(amount - len(data))
        if not chunk:
            break
        data += chunk
    return data


def receive_message(sock: socket.socket) -> Optional[bytes]:
    raw_len = _recv_exact(sock, HEADER_SIZE)
    if not raw_len:
        return None
    try:
        amount_expected = int(raw_len.decode('utf-8'))
    except ValueError:
        return None
    data = _recv_exact(sock, amount_expected)
    if len(data) != amount_expected:
        return None
    return data


def split_message(data: bytes) -> Tuple[str, str]:
    service = data[:SERVICE_SIZE].decode('utf-8')
    payload = data[SERVICE_SIZE:].decode('utf-8')
    return service, payload
