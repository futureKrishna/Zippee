import unittest
from app import create_app
from app.extensions import db
from app.models import User, Task
from flask_jwt_extended import create_access_token

class TasksTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            user = User(username='testuser')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id
            self.token = create_access_token(identity=str(user.id))
            # No Bearer prefix - just the token
            self.headers = {'Authorization': self.token}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_and_get_task(self):
        # Create
        res = self.client.post('/tasks', json={'title': 'Test Task'}, headers=self.headers)
        print('CREATE RESPONSE:', res.status_code, res.get_json())
        self.assertEqual(res.status_code, 201)
        task_id = res.get_json()['id']
        # Get
        res = self.client.get(f'/tasks/{task_id}', headers=self.headers)
        print('GET RESPONSE:', res.status_code, res.get_json())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['title'], 'Test Task')

    def test_update_and_delete_task(self):
        # Create
        res = self.client.post('/tasks', json={'title': 'Task'}, headers=self.headers)
        print('CREATE RESPONSE:', res.status_code, res.get_json())
        task_id = res.get_json()['id']
        # Update
        res = self.client.put(f'/tasks/{task_id}', json={'completed': True}, headers=self.headers)
        print('UPDATE RESPONSE:', res.status_code, res.get_json())
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()['completed'])
        # Delete
        res = self.client.delete(f'/tasks/{task_id}', headers=self.headers)
        print('DELETE RESPONSE:', res.status_code, res.get_json())
        self.assertEqual(res.status_code, 200)
        # Confirm delete
        res = self.client.get(f'/tasks/{task_id}', headers=self.headers)
        print('CONFIRM DELETE RESPONSE:', res.status_code, res.get_json())
        self.assertEqual(res.status_code, 404)

    def test_get_task_not_found(self):
        res = self.client.get('/tasks/9999', headers=self.headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn('msg', res.get_json())

    def test_delete_task_twice(self):
        # Create
        res = self.client.post('/tasks', json={'title': 'Task'}, headers=self.headers)
        task_id = res.get_json()['id']
        # Delete
        res = self.client.delete(f'/tasks/{task_id}', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        # Delete again
        res = self.client.delete(f'/tasks/{task_id}', headers=self.headers)
        self.assertEqual(res.status_code, 404)

    def test_update_task_invalid_data(self):
        # Create
        res = self.client.post('/tasks', json={'title': 'Task'}, headers=self.headers)
        task_id = res.get_json()['id']
        # Update with invalid data
        res = self.client.put(f'/tasks/{task_id}', json={'completed': 'notabool'}, headers=self.headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn('msg', res.get_json())

    def test_get_tasks_pagination_and_filter(self):
        # Create multiple tasks
        for i in range(15):
            self.client.post('/tasks', json={'title': f'Task {i}', 'completed': i % 2 == 0}, headers=self.headers)
        # Get first page
        res = self.client.get('/tasks?page=1&per_page=5', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data['tasks']), 5)
        self.assertEqual(data['current_page'], 1)
        # Get second page
        res = self.client.get('/tasks?page=2&per_page=5', headers=self.headers)
        data = res.get_json()
        self.assertEqual(data['current_page'], 2)
        # Filter completed tasks
        res = self.client.get('/tasks?completed=true', headers=self.headers)
        data = res.get_json()
        for task in data['tasks']:
            self.assertTrue(task['completed'])

    def test_create_task_missing_title(self):
        res = self.client.post('/tasks', json={'description': 'No title'}, headers=self.headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn('msg', res.get_json())

    def test_update_nonexistent_task(self):
        res = self.client.put('/tasks/9999', json={'title': 'Nope'}, headers=self.headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn('msg', res.get_json())

    def test_delete_nonexistent_task(self):
        res = self.client.delete('/tasks/9999', headers=self.headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn('msg', res.get_json())

    def test_unauthorized_access(self):
        res = self.client.get('/tasks')
        self.assertEqual(res.status_code, 401)
        res = self.client.post('/tasks', json={'title': 'No Auth'})
        self.assertEqual(res.status_code, 401)

    def test_options_tasks(self):
        res = self.client.options('/tasks', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        res = self.client.options('/tasks/1', headers=self.headers)
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
