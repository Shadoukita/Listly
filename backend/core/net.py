"""
SSRF-safe outbound HTTP.

Any request made on behalf of a user-supplied URL (recipe import, image
download by URL) MUST go through fetch_external(). Never call requests.get()
or urllib.request.urlopen() directly on user input.

Guarantees
----------
* http / https only — blocks file://, ftp://, gopher:// and friends.
* Every address the hostname resolves to must be public — blocks loopback,
  private ranges, link-local (169.254.169.254 cloud metadata), multicast,
  reserved and unspecified addresses, including IPv4-mapped IPv6 forms.
* Redirects are followed manually and each hop is re-validated, so an
  allowed host cannot bounce the request to an internal one.
* The response body is hard-capped; oversized bodies are abandoned mid-stream.

Residual risk: a DNS name whose record flips between the validation lookup and
the connection (DNS rebinding) is not defeated by name-based validation. That
requires attacker-controlled DNS with a near-zero TTL and precise timing.
"""
import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests

_ALLOWED_SCHEMES = {"http", "https"}
_MAX_REDIRECTS   = 3
_TIMEOUT         = 10
_CHUNK           = 64 * 1024


class UnsafeURLError(ValueError):
    """A user-supplied URL that must not be fetched."""


def _ip_is_public(raw: str) -> bool:
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError:
        return False
    # ::ffff:127.0.0.1 must be judged on the embedded IPv4 address
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped:
        ip = mapped
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _validate(url: str) -> None:
    """Raise UnsafeURLError unless url is http(s) and resolves only to public IPs."""
    parsed = urlparse(url)
    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        raise UnsafeURLError("only http and https URLs are allowed")

    host = parsed.hostname
    if not host:
        raise UnsafeURLError("URL has no host")

    port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError, ValueError):
        raise UnsafeURLError("host could not be resolved") from None
    if not infos:
        raise UnsafeURLError("host could not be resolved")

    for info in infos:
        if not _ip_is_public(info[4][0]):
            raise UnsafeURLError("URL resolves to a non-public address")


def fetch_external(url: str, *, max_bytes: int, headers: dict | None = None) -> tuple[bytes, str]:
    """
    Fetch a user-supplied URL. Returns (body, content_type).

    Raises UnsafeURLError for a URL we refuse to touch, or
    requests.RequestException for an ordinary network/HTTP failure.
    """
    current   = url
    redirects = 0

    while True:
        _validate(current)
        resp = requests.get(
            current,
            headers=headers or {},
            timeout=_TIMEOUT,
            allow_redirects=False,
            stream=True,
        )
        try:
            if resp.is_redirect or resp.is_permanent_redirect:
                location = resp.headers.get("Location")
                if not location:
                    raise UnsafeURLError("redirect without a target")
                redirects += 1
                if redirects > _MAX_REDIRECTS:
                    raise UnsafeURLError("too many redirects")
                current = urljoin(current, location)
                continue

            resp.raise_for_status()

            body = bytearray()
            for chunk in resp.iter_content(_CHUNK):
                body.extend(chunk)
                if len(body) > max_bytes:
                    raise UnsafeURLError("response body too large")

            ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return bytes(body), ctype
        finally:
            resp.close()
