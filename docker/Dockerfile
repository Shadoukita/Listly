# ── Stage 1: Build Vue frontend ─────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /build
# Copy only manifests first so npm ci layer is cached unless deps change
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python backend with Gunicorn ───────────────────────────────
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy built frontend to where Flask looks for it (DIST_DIR env var)
COPY --from=frontend-build /build/dist /frontend/dist

# Default unprivileged identity. The container still STARTS as root so the
# entrypoint can fix ownership of a bind-mounted /data before dropping to this
# user (or to PUID/PGID).
#
# Declaring `USER listly` here instead would break every bind mount: a
# Dockerfile chown only affects the image layer, while a host mount keeps the
# host's ownership. On Unraid /mnt/user/appdata is nobody:users (99:100), which
# a fixed uid cannot write to — SQLite then fails with
# "attempt to write a readonly database".
RUN useradd --system --create-home --uid 10001 listly

RUN mkdir -p /data/assets/recipes /data/assets/users \
    && chown -R listly:listly /data /app

COPY docker/entrypoint.py /usr/local/bin/docker-entrypoint.py
# This repo is developed on Windows. If the entrypoint is ever checked out with
# CRLF, the kernel reads the shebang as "python3\r", fails to find it, and the
# container dies with exit 127 before printing a single line. Strip CR, then
# prove the result is a valid script rather than discovering it at runtime.
RUN sed -i "s/\r$//" /usr/local/bin/docker-entrypoint.py \
    && chmod +x /usr/local/bin/docker-entrypoint.py \
    && python3 -c "import ast,pathlib;ast.parse(pathlib.Path('/usr/local/bin/docker-entrypoint.py').read_text())"

ENV DATABASE=/data/database.db
ENV DIST_DIR=/frontend/dist
ENV ASSETS_DIR=/data/assets
ENV PORT=5000
# Persist an auto-generated SECRET_KEY on the volume. Without this it lands in
# the container's writable layer and is regenerated on every image upgrade,
# invalidating every session. Passing SECRET_KEY explicitly still takes priority.
ENV ENV_FILE=/data/.env

# Run the app as a specific account. Unraid exposes these in its template.
# Left unset, the entrypoint adopts whoever already owns /data, so an existing
# bind mount keeps working with no configuration.
ENV PUID=""
ENV PGID=""

EXPOSE ${PORT}

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.py"]

# 2 workers is fine for a home server; raise if you need more concurrency
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 60 --access-logfile - main:app"]
