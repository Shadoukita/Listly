# Deployment

## What you need

- Docker + Docker Compose
- A `SECRET_KEY` — any long random string, used to sign JWTs

---

## Docker Compose (the normal way)

**1. Environment file**

```bash
cp docker/.env.example docker/.env
```

Open `docker/.env` and fill it in:

```env
SECRET_KEY=your-very-long-random-secret-here
HOST_PORT=8080        # port exposed on the host
PORT=5000             # port inside the container (leave this alone)
```

**2. Build and start**

```bash
cd docker
docker compose up -d --build
```

**3. First run**

Open `http://localhost:<HOST_PORT>`. You'll land on the setup wizard — create the admin account there and optionally set the public endpoint URL (used in invite links).

---

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | **required** | Change immediately if it leaks |
| `HOST_PORT` | `8080` | Port on the host machine |
| `PORT` | `5000` | Port Gunicorn listens on inside the container |
| `DATABASE` | `/data/database.db` | SQLite file path |
| `DIST_DIR` | `/frontend/dist` | Built Vue app |
| `ASSETS_DIR` | `/data/assets` | Uploaded images |

---

## Persistent data

A named volume `listly_data` is mounted at `/data` inside the container:

```
/data/
├── database.db
└── assets/
    ├── recipes/
    └── users/
```

Back this up before moving hosts.

```bash
# Backup
docker run --rm -v listly_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/listly_backup.tar.gz /data

# Restore
docker run --rm -v listly_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/listly_backup.tar.gz -C /
```

---

## Upgrades

```bash
cd docker
docker compose up -d --build
```

Database migrations run automatically on startup, no manual SQL needed.

---

## Running without Docker (dev)

**Backend**

```bash
cd backend
pip install -r requirements.txt
export SECRET_KEY=dev-secret
python main.py          # Flask dev server on :5000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev             # Vite on :5173, proxies /api → :5000
```

**Production build**

```bash
cd frontend
npm run build           # outputs to frontend/dist/
```

Flask serves `frontend/dist/index.html` for all non-API routes.

---

## Reverse proxy (nginx example)

```nginx
server {
    listen 443 ssl;
    server_name list.example.com;

    location / {
        proxy_pass         http://127.0.0.1:8080;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-Proto https;
        client_max_body_size 20M;
    }
}
```

Set the **Endpoint URL** in the admin panel to your public domain so invite links are generated correctly.
