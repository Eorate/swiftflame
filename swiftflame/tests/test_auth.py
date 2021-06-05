import json
import unittest

from swiftflame.models.models import User
from swiftflame.swiftflame import app
from swiftflame.views.main import db_session


class TestCaseAuthEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.db_session = db_session

    def tearDown(self):
        self.db_session.query(User).delete()
        self.db_session.commit()

    def test_encode_access_token(self):
        # When we write decode we can change to below kind of test
        # https://github.com/jpadilla/pyjwt/blob/master/tests/test_jwt.py
        user = User(email="pluto@example.com", password="pluto123")
        self.db_session.add(user)
        self.db_session.commit()
        auth_token = user.encode_auth_token(user.id, app.config)
        self.assertTrue(isinstance(auth_token, str))

    def test_register_a_new_user(self):
        """Test POST /auth/register
        Register a new user
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="scooby@example.com", password="123456")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertTrue(data["message"] == "Successfully registered.")
        self.assertTrue(data["auth_token"])
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 201)

    def test_register_a_new_user_with_missing_data_fails(self):
        """Test POST /auth/register
        Try to register a user but dont provide a password
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="scooby@example.com")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertTrue(data["message"] == "Some error occurred. Please try again.")
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 401)

    def test_register_an_existing_user_fails(self):
        """Test POST /auth/register
        Attempting to register an existing user should fail.
        """
        user = User(email="scrapy@example.com", password="scrapy123456")
        self.db_session.add(user)
        self.db_session.commit()

        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="scrapy@example.com", password="scrapy123456")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertTrue(data["message"] == "User already exists. Please Log in.")
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 202)
