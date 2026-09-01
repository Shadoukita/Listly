import glob
import os
import re
import secrets

from flask import g, jsonify, request

from api.uploads import bp
from core.config import ASSETS_DIR
from core.images import sniff_image_ext
from core.net import UnsafeURLError, fetch_external
from core.security import token_required
from core.utils import ROLE_RANK, get_member_role
from lang.lang_config import t
from db.session import get_db

_ALLOWED    = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
_SUBFOLDERS = {"recipe": "recipes", "user": "users"}
_MAX_BYTES  = 10 * 1024 * 1024

# Resource IDs name a row's primary key, so they are always digits. Anything
# else — a path separator, "..", a drive letter, an absolute path — is rejected
# outright rather than sanitised, because os.path.join() silently discards the
# destination directory when handed an absolute path.
_RESOURCE_ID_RE = re.compile(r"^[0-9]{1,18}$")

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Listly/1.0)"}


def _safe_path(dest_dir: str, filename: str) -> str:
    """
    Resolve filename inside dest_dir, refusing anything that escapes it.

    Belt-and-braces behind _RESOURCE_ID_RE: no path we build may ever leave the
    assets folder, whatever the caller sends.
    """
    root = os.path.realpath(dest_dir)
    path = os.path.realpath(os.path.join(root, filename))
    if path != root and not path.startswith(root + os.sep):
        raise ValueError("path escapes the assets directory")
    return path


def _may_write(upload_type: str, resource_id: str) -> bool:
    """
    True if the current user is allowed to replace this resource's image.

    Without this any logged-in user could overwrite another member's avatar or
    any household's recipe image just by naming its ID.
    """
    if g.current_user.get("role") == "admin":
        return True

    if upload_type == "user":
        return str(g.current_user["id"]) == resource_id

    # Recipe images: same bar as editing the recipe itself (see recipes/update.py)
    row = get_db().execute(
        "SELECT household_id FROM recipes WHERE id = ?", (int(resource_id),)
    ).fetchone()
    if not row:
        return False
    role = get_member_role(row["household_id"])
    return bool(role) and ROLE_RANK.get(role, 0) >= ROLE_RANK["member"]


def _replace_old(dest_dir: str, resource_id: str, new_ext: str) -> None:
    """Delete any existing file for this resource ID (handles extension changes)."""
    root = os.path.realpath(dest_dir)
    for path in glob.glob(os.path.join(root, f"{resource_id}.*")):
        resolved = os.path.realpath(path)
        if not resolved.startswith(root + os.sep):
            continue
        if os.path.splitext(resolved)[1].lower() != new_ext:
            try:
                os.remove(resolved)
            except OSError:
                pass


@bp.post("/upload")
@token_required
def upload_file():
    upload_type = request.form.get("type", "recipe")
    resource_id = request.form.get("id", "").strip()
    subfolder   = _SUBFOLDERS.get(upload_type, "recipes")
    dest_dir    = os.path.join(ASSETS_DIR, subfolder)
    os.makedirs(dest_dir, exist_ok=True)

    if resource_id:
        if not _RESOURCE_ID_RE.match(resource_id):
            return jsonify({"error": t("error.invalid_resource_id")}), 400
        if not _may_write(upload_type, resource_id):
            return jsonify({"error": t("error.no_access")}), 403

    # ── URL download mode ────────────────────────────────────────────────────
    source_url = request.form.get("url", "").strip()
    if source_url:
        try:
            data, _ = fetch_external(source_url, max_bytes=_MAX_BYTES, headers=_HEADERS)
        except UnsafeURLError:
            return jsonify({"error": t("error.image_url_not_allowed")}), 400
        except Exception:
            return jsonify({"error": t("error.image_download_fail")}), 400
    else:
        # ── File upload mode ─────────────────────────────────────────────────
        if "file" not in request.files:
            return jsonify({"error": t("error.no_file")}), 400
        f = request.files["file"]
        if not f.filename:
            return jsonify({"error": t("error.no_filename")}), 400
        if os.path.splitext(f.filename)[1].lower() not in _ALLOWED:
            return jsonify({"error": t("error.invalid_file_type")}), 400
        data = f.read(_MAX_BYTES + 1)
        if len(data) > _MAX_BYTES:
            return jsonify({"error": t("error.file_too_large")}), 400

    # The extension comes from the bytes, never from the caller's filename or
    # URL — these files are served back from our own origin.
    ext = sniff_image_ext(data)
    if not ext:
        return jsonify({"error": t("error.invalid_file_type")}), 400

    if resource_id:
        _replace_old(dest_dir, resource_id, ext)
        filename = resource_id + ext
    else:
        filename = secrets.token_hex(16) + ext

    try:
        target = _safe_path(dest_dir, filename)
    except ValueError:
        return jsonify({"error": t("error.invalid_resource_id")}), 400

    with open(target, "wb") as fh:
        fh.write(data)
    return jsonify({"url": f"/assets/{subfolder}/{filename}"})
