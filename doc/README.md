# Listly

Listly is a self-hosted app for managing household shopping lists and recipes. You can be in multiple households at once and switch between them — each one has its own list and cookbook.

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Vue 3, Vite, Pinia, Vue Router, Vue i18n |
| Backend | Python 3.12, Flask, SQLite |
| Auth | JWT (PyJWT), PBKDF2-SHA256 |
| Serving | Gunicorn (2 workers) |
| Container | Docker, multi-stage build |

---

## Repository layout

```
Listly/
├── backend/
│   ├── api/        # route blueprints
│   ├── core/       # config, security, utilities
│   ├── db/         # schema, models, migrations
│   ├── lang/       # backend i18n (en_US / de_DE)
│   └── app.py      # application factory
│
├── frontend/
│   └── src/
│       ├── views/      # page components
│       ├── components/ # shared UI
│       ├── stores/     # Pinia stores
│       └── lang/       # translation files
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── doc/            # you are here
```

---

## Quick start

```bash
cp docker/.env.example docker/.env
# set SECRET_KEY and HOST_PORT in docker/.env

cd docker
docker compose up -d --build
```

Open `http://localhost:<HOST_PORT>` — on first visit it'll walk you through creating the admin account.

Full deployment notes are in `doc/DEPLOYMENT.md`.

---

## Modules

Listly has a module system so you can turn features on or off. Right now there are two:

| Module | What it does |
|---|---|
| `shopping` | shared shopping list per household |
| `recipes` | household recipe cookbook with URL import |

Admins toggle them globally; users can also disable ones they don't personally use.

---

## Roles

Every household member has a role. Roles are per-household — you can be an owner in one and a restricted member in another.

| Role | Rank | What you can do |
|---|---|---|
| `owner` | 4 | everything — rename/delete household, manage member roles |
| `admin` | 3 | kick members, edit/delete any recipe |
| `member` | 2 | add/edit recipes, manage shopping list |
| `restricted` | 1 | view only |

There's also a global `admin` flag on user accounts (separate from household roles) that gives access to the instance admin panel.

---

## Further reading

- `doc/ARCHITECTURE.md` — how the pieces fit together
- `doc/DEPLOYMENT.md` — running in production
- `doc/API.md` — every endpoint documented
- `backend/doc/README.md` — backend internals
- `frontend/doc/README.md` — frontend internals
