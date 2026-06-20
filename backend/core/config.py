import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/

DIST_DIR   = os.environ.get(
    "DIST_DIR",
    os.path.join(BASE_DIR, "..", "frontend", "dist"),
)
DATABASE   = os.environ.get("DATABASE",   os.path.join(BASE_DIR, "database.db"))
ASSETS_DIR = os.environ.get("ASSETS_DIR", os.path.join(BASE_DIR, "assets"))
PORT       = int(os.environ.get("PORT", 5000))
SECRET_KEY = os.environ["SECRET_KEY"]  # guaranteed set by main.py before import

MODULES = ["shopping", "recipes", "mealplanner", "storage"]
