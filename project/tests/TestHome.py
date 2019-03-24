from project.server import app
from unittest import TestCase
import json

class TestIntegrations(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_thing(self):
        response = self.app.get('/')
        data = json.loads(response.data)
        assert data["hello"] == "world"
