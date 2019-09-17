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

        # Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySWQiOiIxMTExMSIsIlVzZXJuYW1lIjoidGVzdEFkbWluIn0.9VgNkIVQgCluHUQgpit8YQp0WaZf5q3F_h7GcdMqLJ0

    def test_secured_hello_world_with_user_from_auth(self):
        with self.client:
            token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySWQiOiIxMTExMSIsIlVzZXJuYW1lIjoidGVzdEFkbWluIn0.9VgNkIVQgCluHUQgpit8YQp0WaZf5q3F_h7GcdMqLJ0'
            User.delete_one('testAdmin')
            resp_register = register_user(self, 'testAdmin', 'joe@gmail.com', 'password2')
            response = self.client.get(
                '/hello_secured?user=me',
                headers=dict(
                    Authorization='Bearer ' + token
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data is not None)
            self.assertTrue(data['hello'] == 'world me')
            self.assertEqual(response.status_code, 200)
            User.delete_one('joe')

    # 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1Njg3MjM5ODcsImlhdCI6MTU2ODcyMzk4Miwic3ViIjoiNWQ4MGQ0MGU5NDhjMjEzOWQxYjA1YTY5In0.DApw9Su9T6CfNFZRdpy6OBJGsT2NJpKPBVgVZHWcCPQ'
    # Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySWQiOiI1ZDVhOGQxMWY0YTU2YTQxMmZiODYzNGIifQ.pTtt23MLnnHxScxQCfx-xL_uHdw_fn2Siunb4PdcaGg
    def test_secured_hello_world1(self):
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

    def test_secured_hello_world2(self):
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

    def test_secured_hello_world3(self):
        with self.client:
            User.delete_one('joe')
            response = self.client.get(
                '/hello_secured?user=me'
            )
            self.assertEqual(response.status_code, 401)
            User.delete_one('joe')