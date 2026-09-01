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

# Run as an unprivileged user — the app writes files it fetches on a user's
# behalf, and none of that should ever land as root.
RUN useradd --system --create-home --uid 10001 listly

# /data is mounted as a Docker volume — database and uploads live here.
# A *fresh* named volume inherits this ownership; a volume created by an older
# root-running image keeps its old ownership, so on upgrade run once:
#   docker run --rm -v listly_data:/data alpine chown -R 10001:10001 /data
RUN mkdir -p /data/assets/recipes /data/assets/users \
    && chown -R listly:listly /data /app

ENV DATABASE=/data/database.db
ENV DIST_DIR=/frontend/dist
ENV ASSETS_DIR=/data/assets
ENV PORT=5000

USER listly

EXPOSE ${PORT}

# 2 workers is fine for a home server; raise if you need more concurrency
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 60 --access-logfile - main:app"]
