from .api_routes import api_bp
from .db_routes import db_bp
from .plots import plots_bp

def register_routes(app):
    app.register_blueprint(api_bp)
    app.register_blueprint(db_bp)
    app.register_blueprint(plots_bp)
