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

# /data is mounted as a Docker volume — database and uploads live here
RUN mkdir -p /data/assets/recipes /data/assets/users

ENV DATABASE=/data/database.db
ENV DIST_DIR=/frontend/dist
ENV ASSETS_DIR=/data/assets
ENV PORT=5000

EXPOSE ${PORT}

# 2 workers is fine for a home server; raise if you need more concurrency
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 60 --access-logfile - main:app"]
