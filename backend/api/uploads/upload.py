import glob
import os
import secrets
import urllib.request
from urllib.error import URLError

from flask import jsonify, request

from api.uploads import bp
from core.config import ASSETS_DIR
from core.security import token_required
from lang.lang_config import t

_ALLOWED     = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
_SUBFOLDERS  = {"recipe": "recipes", "user": "users"}
_MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png":  ".png",
    "image/webp": ".webp",
    "image/gif":  ".gif",
}


def _replace_old(dest_dir: str, resource_id: str, new_ext: str) -> None:
    """Delete any existing file for this resource ID (handles extension changes)."""
    for path in glob.glob(os.path.join(dest_dir, f"{resource_id}.*")):
        if os.path.splitext(path)[1].lower() != new_ext:
            try:
                os.remove(path)
            except OSError:
                pass


def _ext_from_url(image_url: str) -> str:
    path_part = image_url.split("?")[0]
    ext = os.path.splitext(path_part)[1].lower()
    return ext if ext in _ALLOWED else ".jpg"


def _download_url(image_url: str) -> tuple[bytes, str] | None:
    """Fetch an external image. Returns (data, ext) or None on failure."""
    try:
        req = urllib.request.Request(
            image_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Listly/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            ext = _MIME_TO_EXT.get(resp.headers.get_content_type()) or _ext_from_url(image_url)
            data = resp.read(10 * 1024 * 1024)  # max 10 MB
        return data, ext
    except (URLError, Exception):
        return None


@bp.post("/upload")
@token_required
def upload_file():
    upload_type = request.form.get("type", "recipe")
    resource_id = request.form.get("id", "").strip()
    subfolder   = _SUBFOLDERS.get(upload_type, "recipes")
    dest_dir    = os.path.join(ASSETS_DIR, subfolder)
    os.makedirs(dest_dir, exist_ok=True)

    # ── URL download mode ────────────────────────────────────────────────────
    source_url = request.form.get("url", "").strip()
    if source_url:
        result = _download_url(source_url)
        if not result:
            return jsonify({"error": t("error.image_download_fail")}), 400
        data, ext = result
        if resource_id:
            _replace_old(dest_dir, resource_id, ext)
            filename = resource_id + ext
        else:
            filename = secrets.token_hex(16) + ext
        with open(os.path.join(dest_dir, filename), "wb") as fh:
            fh.write(data)
        return jsonify({"url": f"/assets/{subfolder}/{filename}"})

    # ── File upload mode ─────────────────────────────────────────────────────
    if "file" not in request.files:
        return jsonify({"error": t("error.no_file")}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": t("error.no_filename")}), 400

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in _ALLOWED:
        return jsonify({"error": t("error.invalid_file_type")}), 400

    if resource_id:
        _replace_old(dest_dir, resource_id, ext)
        filename = resource_id + ext
    else:
        filename = secrets.token_hex(16) + ext

    f.save(os.path.join(dest_dir, filename))
    return jsonify({"url": f"/assets/{subfolder}/{filename}"})
