from project.server import app
from project.tests.base_test import BaseTestCase
from project.tests.test_auth import register_user, login_user
from project.server.models import User, BlacklistToken

import json

class TestIntegrations(BaseTestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_thing(self):
        response = self.client.get('/hi?user=me')
        data = json.loads(response.data.decode())
        assert data["hello"] == "world me"

    def test_secured_hello_world(self):
        with self.client:
            User.delete_one('joe')
            resp_register = register_user(self, 'joe', 'joe@gmail.com', '123456')
            response = self.client.get(
                '/hello_secured?user=me',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data is not None)
            self.assertTrue(data['hello'] == 'world me')
            self.assertEqual(response.status_code, 200)
            User.delete_one('joe')

    def test_secured_hello_world(self):
        with self.client:
            User.delete_one('joe')
            response = self.client.get(
                '/hello_secured?user=me',
                headers=dict(
                    Authorization='Bearer ' + '-----'
                )
            )
            self.assertEqual(response.status_code, 401)
            User.delete_one('joe')

    def test_secured_hello_world(self):
        with self.client:
            User.delete_one('joe')
            response = self.client.get(
                '/hello_secured?user=me'
            )
            self.assertEqual(response.status_code, 401)
            User.delete_one('joe')