# blueprints to keep our code separated

from routes.api_routes import api_bp
from routes.db_routes import db_bp
from routes.plots import plots_bp
from routes.get_db_connection import get_db_connection
from routes import register_routes


def register_routes(app):
    app.register_blueprint(api_bp)
    app.register_blueprint(db_bp)
    app.register_blueprint(plots_bp)