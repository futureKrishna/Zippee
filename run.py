#!/usr/bin/env python3
"""
Task Manager API Application Entry Point

This module starts the Flask application for the Task Manager API.
It can be run directly for development or used with a WSGI server for production.
"""

import os
from app import create_app

# Get configuration from environment
config_name = os.environ.get('FLASK_ENV', 'development')

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Task Manager API on port {port}")
    print(f"📚 API Documentation: http://localhost:{port}/swagger/")
    print(f"🏥 Health Check: http://localhost:{port}/")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
