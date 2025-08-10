from flask import Flask, jsonify
from .extensions import db, migrate, jwt
from .routes import register_routes
from .routes.swagger import swagger_bp
from .__version__ import __version__, __description__
import os

def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'development':
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        # Fallback to the Config class for backward compatibility
        app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register routes
    register_routes(app)
    app.register_blueprint(swagger_bp, url_prefix='/swagger')
    
    # Serve static files for swagger.json
    @app.route('/static/<path:filename>')
    def staticfiles(filename):
        return app.send_static_file(filename)
    
    # Health check endpoint
    @app.route('/')
    def health():
        return {
            'status': 'ok', 
            'message': 'Task Manager API is running!',
            'version': __version__,
            'description': __description__,
            'environment': config_name
        }, 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app
