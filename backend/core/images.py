"""
Image content validation.

A filename extension is attacker-controlled and proves nothing about the bytes.
Uploads are served back from the app's own origin, so the stored bytes must be
confirmed to be a real image before they are written to disk.

sniff_image_ext() returns the canonical extension for the detected format, or
None if the bytes are not one of the formats we accept.
"""

# Magic-byte prefixes, longest-first where prefixes could overlap.
_SIGNATURES: list[tuple[bytes, str]] = [
    (b"\xff\xd8\xff",             ".jpg"),   # JPEG (JFIF / Exif / raw)
    (b"\x89PNG\r\n\x1a\n",        ".png"),   # PNG
    (b"GIF87a",                   ".gif"),   # GIF
    (b"GIF89a",                   ".gif"),
]

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def sniff_image_ext(data: bytes) -> str | None:
    """Return the canonical extension for these bytes, or None if not an image."""
    for signature, ext in _SIGNATURES:
        if data.startswith(signature):
            return ext
    # WebP: "RIFF" <4-byte size> "WEBP"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None
