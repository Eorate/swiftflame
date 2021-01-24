import unittest
from swiftflame.swiftflame import app


class TestCaseEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
