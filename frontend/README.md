# Listly — New Frontend

Redesigned Vue 3 frontend with a dark-only design system, Geist font, and inline SVG icons.

## Dev

Start the Flask backend first (port 5000), then:

```bash
cd frontend-new
npm install
npm run dev
```

The Vite dev server runs on port 5173 and proxies `/api` and `/uploads` to `localhost:5000`.

## Build

```bash
npm run build
# Output → frontend-new/dist/
```

## Switch between old and new frontend

The backend reads the `LISTLY_FRONTEND` env var:

```bash
# Serve the new frontend
LISTLY_FRONTEND=new python backend/app.py

# Serve the old frontend (default)
python backend/app.py
```

Or set `DIST_DIR` directly to any dist folder:

```bash
DIST_DIR=/absolute/path/to/dist python backend/app.py
```

## Recipe URL import

Install the optional scraper library for the import-from-URL feature:

```bash
pip install recipe-scrapers>=14.0
```

Without it the `/api/recipes/import` endpoint returns 501.

## Image uploads

Uploaded files go to `backend/uploads/`. Served at `/uploads/<filename>`.
