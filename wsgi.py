"""WSGI entrypoint for production servers (Gunicorn/Render)."""

from app import create_app
from models import db

app = create_app()

# Ensure tables exist on first boot (useful for fresh Render deployments).
with app.app_context():
    db.create_all()

