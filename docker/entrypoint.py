#!/usr/bin/env python3
"""
Container entrypoint: prepare /data, then drop root before running the app.

Why this exists
───────────────
The image should not run the app as root, but it also cannot simply declare
`USER listly` in the Dockerfile. A Dockerfile chown only affects the image
layer; a bind-mounted host directory replaces it wholesale and keeps the
host's ownership. On Unraid, /mnt/user/appdata is nobody:users (99:100), so a
fixed uid could not write to it and SQLite failed with
"attempt to write a readonly database".

So the container starts as root, works out which uid should own the data, fixes
what it needs to, and only then drops privileges.

Choosing the uid
────────────────
  PUID / PGID        explicit override; always wins (Unraid exposes these)
  otherwise          adopt whatever already owns the data directory, so a
                     bind mount keeps its existing ownership and the operator
                     has nothing to configure
  root-owned / new   fall back to the image's own `listly` user (10001)

Never runs the app as root. If the container was started with --user, the
privilege drop is skipped because it has already happened.
"""
import os
import sys

FALLBACK_UID = 10001
FALLBACK_GID = 10001


def _int_env(name):
    raw = (os.environ.get(name) or "").strip()
    try:
        return int(raw) if raw else None
    except ValueError:
        print(f"[entrypoint] ignoring non-numeric {name}={raw!r}", flush=True)
        return None


def _chown(path, uid, gid):
    try:
        os.chown(path, uid, gid)
    except OSError:
        pass  # read-only mount or unsupported fs — surfaced later if fatal


def main():
    argv = sys.argv[1:]
    if not argv:
        print("[entrypoint] no command given", file=sys.stderr)
        return 1

    data = os.environ.get("DATA_DIR", "/data")
    try:
        os.makedirs(data, exist_ok=True)
    except OSError as exc:
        print(f"[entrypoint] cannot create {data}: {exc}", file=sys.stderr)

    try:
        st = os.stat(data)
        owner_uid, owner_gid = st.st_uid, st.st_gid
    except OSError:
        owner_uid = owner_gid = 0

    # Never adopt root as the run user — fall back to the image's own account.
    uid = _int_env("PUID") or (owner_uid if owner_uid else FALLBACK_UID)
    gid = _int_env("PGID") or (owner_gid if owner_gid else FALLBACK_GID)
    if uid == 0:
        uid = FALLBACK_UID
    if gid == 0:
        gid = FALLBACK_GID

    if os.geteuid() == 0:
        for sub in ("assets", "assets/recipes", "assets/users"):
            try:
                os.makedirs(os.path.join(data, sub), exist_ok=True)
            except OSError:
                pass

        # Targeted rather than a blanket -R: appdata can be large, and this
        # runs on every start.
        _chown(data, uid, gid)
        for name in ("database.db", "database.db-wal", "database.db-shm", ".env"):
            path = os.path.join(data, name)
            if os.path.exists(path):
                _chown(path, uid, gid)
        for root, dirs, files in os.walk(os.path.join(data, "assets")):
            _chown(root, uid, gid)
            for f in files:
                _chown(os.path.join(root, f), uid, gid)

        print(f"[entrypoint] running as uid={uid} gid={gid} (data={data})", flush=True)
        try:
            os.setgroups([gid])
            os.setgid(gid)
            os.setuid(uid)
        except OSError as exc:
            print(f"[entrypoint] could not drop to {uid}:{gid}: {exc}", file=sys.stderr)
            return 1
    else:
        print(f"[entrypoint] already non-root (uid={os.geteuid()})", flush=True)

    os.execvp(argv[0], argv)


if __name__ == "__main__":
    sys.exit(main())
