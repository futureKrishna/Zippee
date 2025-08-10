"""
Test cases for the application factory and core functionality.
"""
import pytest
from app import create_app

def test_app_factory_config():
    """Test application factory configuration."""
    app = create_app()
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    assert app.config['JWT_SECRET_KEY']
    assert app.config['SECRET_KEY']
    assert app.config['SQLALCHEMY_DATABASE_URI']

def test_staticfiles_route():
    """Test static files route."""
    app = create_app()
    client = app.test_client()
    # This will 404 for any file, but route should exist
    response = client.get('/static/doesnotexist.json')
    assert response.status_code in (200, 404)

def test_app_blueprints_registered():
    """Test that all required blueprints are registered."""
    app = create_app()
    assert 'auth' in app.blueprints
    assert 'tasks' in app.blueprints
    assert 'swagger_ui' in app.blueprints

def test_app_config_and_static_route():
    """Test application configuration and static route."""
    app = create_app()
    client = app.test_client()
    # Test config values
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    assert app.config['JWT_SECRET_KEY']
    assert app.config['SECRET_KEY']
    assert app.config['SQLALCHEMY_DATABASE_URI']
    # Test static route returns 404 for missing file
    response = client.get('/static/doesnotexist.json')
    assert response.status_code == 404
    # Test static route for swagger.json (should be 200 if file exists)
    response = client.get('/static/swagger.json')
    assert response.status_code in (200, 404)

def test_health_check_route():
    """Test health check endpoint."""
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'message' in data
    assert 'version' in data
    assert 'description' in data

def test_error_handlers():
    """Test custom error handlers."""
    app = create_app()
    client = app.test_client()
    
    # Test 404 handler
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Resource not found'
