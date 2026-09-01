#!/usr/bin/env python3
"""
Container entrypoint: prepare the data directory, then drop root before
running the app.

Why this exists
───────────────
The image should not run the app as root, but it also cannot simply declare
`USER listly` in the Dockerfile. A Dockerfile chown only affects the image
layer; a bind-mounted host directory replaces it wholesale and keeps the
host's ownership. On Unraid /mnt/user/appdata is nobody:users (99:100), so a
fixed uid could not write to it and SQLite failed with
"attempt to write a readonly database".

So the container starts as root, works out which uid should own the data,
fixes what it needs to, proves the result is actually writable, and only then
drops privileges.

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


def log(msg):
    print(f"[entrypoint] {msg}", flush=True)


def die(msg):
    print(f"[entrypoint] ERROR: {msg}", file=sys.stderr, flush=True)


def _int_env(name):
    raw = (os.environ.get(name) or "").strip()
    try:
        return int(raw) if raw else None
    except ValueError:
        log(f"ignoring non-numeric {name}={raw!r}")
        return None


def _chown(path, uid, gid, problems):
    """chown, recording failures instead of hiding them."""
    try:
        st = os.stat(path)
        if st.st_uid == uid and st.st_gid == gid:
            return
        os.chown(path, uid, gid)
    except OSError as exc:
        problems.append(f"{path}: {exc.strerror}")


def _writable_as(uid, gid, paths):
    """
    Fork a child, drop to uid/gid there, and check the paths are writable.
    Returns a list of paths that are not. Done in a child so the parent keeps
    root and can still repair things.
    """
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        bad = []
        try:
            os.setgroups([gid])
            os.setgid(gid)
            os.setuid(uid)
            for p in paths:
                if os.path.isdir(p):
                    probe = os.path.join(p, ".listly-write-probe")
                    try:
                        with open(probe, "w"):
                            pass
                        os.unlink(probe)
                    except OSError:
                        bad.append(p)
                elif os.path.exists(p):
                    if not os.access(p, os.W_OK):
                        bad.append(p)
        except Exception as exc:  # noqa: BLE001 — report anything at all
            bad.append(f"drop-privileges: {exc}")
        os.write(write_fd, "\n".join(bad).encode())
        os.close(write_fd)
        os._exit(0)

    os.close(write_fd)
    chunks = []
    while True:
        chunk = os.read(read_fd, 4096)
        if not chunk:
            break
        chunks.append(chunk)
    os.close(read_fd)
    os.waitpid(pid, 0)
    out = b"".join(chunks).decode().strip()
    return [line for line in out.split("\n") if line]


def main():
    argv = sys.argv[1:]
    if not argv:
        die("no command given")
        return 1

    data = os.environ.get("DATA_DIR", "/data")
    try:
        os.makedirs(data, exist_ok=True)
    except OSError as exc:
        die(f"cannot create {data}: {exc}")

    try:
        st = os.stat(data)
        owner_uid, owner_gid, mode = st.st_uid, st.st_gid, oct(st.st_mode)[-3:]
    except OSError as exc:
        die(f"cannot stat {data}: {exc}")
        return 1

    uid = _int_env("PUID") or (owner_uid if owner_uid else FALLBACK_UID)
    gid = _int_env("PGID") or (owner_gid if owner_gid else FALLBACK_GID)
    if uid == 0:
        uid = FALLBACK_UID
    if gid == 0:
        gid = FALLBACK_GID

    log(f"{data} is owned by {owner_uid}:{owner_gid} mode {mode}")

    # The database may be configured to live outside the data directory.
    db_path = os.environ.get("DATABASE", os.path.join(data, "database.db"))
    db_dir = os.path.dirname(db_path) or data

    if os.geteuid() == 0:
        problems = []
        for sub in ("assets", "assets/recipes", "assets/users"):
            try:
                os.makedirs(os.path.join(data, sub), exist_ok=True)
            except OSError as exc:
                problems.append(f"{data}/{sub}: {exc.strerror}")

        # Targeted rather than a blanket -R: appdata can be large and this runs
        # on every start.
        _chown(data, uid, gid, problems)
        if db_dir != data:
            try:
                os.makedirs(db_dir, exist_ok=True)
            except OSError:
                pass
            _chown(db_dir, uid, gid, problems)
        for name in ("database.db", "database.db-wal", "database.db-shm", ".env"):
            p = os.path.join(data, name)
            if os.path.exists(p):
                _chown(p, uid, gid, problems)
        for extra in (db_path, db_path + "-wal", db_path + "-shm"):
            if os.path.exists(extra):
                _chown(extra, uid, gid, problems)
        for root, _dirs, files in os.walk(os.path.join(data, "assets")):
            _chown(root, uid, gid, problems)
            for f in files:
                _chown(os.path.join(root, f), uid, gid, problems)

        if problems:
            log(f"could not change ownership of {len(problems)} path(s):")
            for p in problems[:5]:
                log(f"  {p}")

        # Prove it before handing over, so a failure is one clear line rather
        # than a SQLite traceback fifty lines deep.
        targets = list(dict.fromkeys([data, db_dir, db_path]))  # de-duplicated
        bad = _writable_as(uid, gid, targets)
        if bad:
            # Some filesystems ignore or reject chown from inside a container —
            # Unraid's /mnt/user is FUSE (shfs), and data left root-owned by
            # pre-1.2.0 images lands here. Refusing to start would turn an
            # upgrade into an outage, and these installs were already running
            # as root before, so continuing as root is not a regression.
            # Say so loudly and tell the operator how to earn the hardening.
            die(f"{data} is not writable as {uid}:{gid} and ownership could not be changed.")
            for b in bad:
                die(f"  not writable: {b}")
            die("Continuing AS ROOT so the app still starts.")
            die("To run unprivileged, fix the host directory and restart, e.g. on Unraid:")
            die(f"  chown -R {uid}:{gid} /mnt/user/appdata/<your-listly-folder>")
            die("or set PUID/PGID to a user that already owns the data.")
            log("running as uid=0 gid=0 (fallback)")
        else:
            log(f"running as uid={uid} gid={gid} (data={data})")
            try:
                os.setgroups([gid])
                os.setgid(gid)
                os.setuid(uid)
            except OSError as exc:
                die(f"could not drop to {uid}:{gid}: {exc}")
                return 1
    else:
        log(f"already non-root (uid={os.geteuid()}) — skipping privilege drop")

    os.execvp(argv[0], argv)


if __name__ == "__main__":
    sys.exit(main())
