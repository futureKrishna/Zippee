import unittest
from app import create_app
from app.extensions import db
from app.models import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_and_login(self):
        # Register
        res = self.client.post('/auth/register', json={
            'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(res.status_code, 201)
        # Login
        res = self.client.post('/auth/login', json={
            'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('access_token', res.get_json())

    def test_register_existing_user(self):
        # Register first time
        res = self.client.post('/auth/register', json={
            'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(res.status_code, 201)
        # Register again with same username
        res = self.client.post('/auth/register', json={
            'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('msg', res.get_json())

    def test_register_missing_fields(self):
        res = self.client.post('/auth/register', json={'username': 'onlyuser'})
        self.assertEqual(res.status_code, 400)
        res = self.client.post('/auth/register', json={'password': 'onlypass'})
        self.assertEqual(res.status_code, 400)
        res = self.client.post('/auth/register', json={})
        self.assertEqual(res.status_code, 400)

    def test_login_invalid_credentials(self):
        res = self.client.post('/auth/login', json={'username': 'nouser', 'password': 'nopass'})
        self.assertEqual(res.status_code, 401)
        self.assertIn('msg', res.get_json())

    def test_register_and_login_with_role(self):
        # Register
        res = self.client.post('/auth/register', json={
            'username': 'admin', 'password': 'adminpass'})
        self.assertEqual(res.status_code, 201)
        # Login
        res = self.client.post('/auth/login', json={
            'username': 'admin', 'password': 'adminpass'})
        self.assertEqual(res.status_code, 200)
        token = res.get_json()['access_token']
        self.assertIsInstance(token, str)

    def test_login_missing_fields(self):
        res = self.client.post('/auth/login', json={'username': 'nouser'})
        self.assertEqual(res.status_code, 401)
        res = self.client.post('/auth/login', json={'password': 'nopass'})
        self.assertEqual(res.status_code, 401)
        res = self.client.post('/auth/login', json={})
        self.assertEqual(res.status_code, 401)

    def test_register_and_login_json_content_type(self):
        # Register with explicit content-type
        res = self.client.post('/auth/register', json={
            'username': 'jsonuser', 'password': 'jsonpass'}, headers={'Content-Type': 'application/json'})
        self.assertEqual(res.status_code, 201)
        # Login with explicit content-type
        res = self.client.post('/auth/login', json={
            'username': 'jsonuser', 'password': 'jsonpass'}, headers={'Content-Type': 'application/json'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('access_token', res.get_json())

if __name__ == '__main__':
    unittest.main()
