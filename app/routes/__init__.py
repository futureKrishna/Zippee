from .auth import auth_bp
from .tasks import tasks_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
