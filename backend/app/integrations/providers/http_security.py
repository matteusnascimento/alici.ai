from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeProviderURL(ValueError):
    pass


def assert_public_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeProviderURL("URL deve usar http:// ou https:// com host valido")

    host = parsed.hostname.strip().lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        raise UnsafeProviderURL("URL nao pode apontar para localhost")

    candidates: set[str] = set()
    try:
        candidates.add(str(ipaddress.ip_address(host)))
    except ValueError:
        try:
            infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
            candidates.update(info[4][0] for info in infos)
        except socket.gaierror:
            return

    for candidate in candidates:
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
        ):
            raise UnsafeProviderURL("URL nao pode resolver para endereco privado ou local")
