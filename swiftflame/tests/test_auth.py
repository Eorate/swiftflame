import json
import time
import unittest

from swiftflame.models.models import BlacklistToken, User
from swiftflame.swiftflame import app
from swiftflame.views.main import db_session


class TestCaseAuthEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.db_session = db_session

    def tearDown(self):
        self.db_session.query(User).delete()
        self.db_session.query(BlacklistToken).delete()
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
            data=json.dumps(dict(email="scooby@example.com", password="12345678")),
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
        Try to register a user but dont provide required data
        """
        # Password not provided
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="scooby@example.com")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertEqual(
            str(data["message"]), "{'password': ['Password is required.']}"
        )
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 401)

        # Invalid email address
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="scooby", password="12345678")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertEqual(
            str(data["message"]), "{'email': ['Not a valid email address.']}"
        )
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 401)

        # Email not provided
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(password="12345678")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertEqual(str(data["message"]), "{'email': ['Email is required.']}")
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 401)

        # Invalid email and incorrect password length
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="scooby", password="")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertEqual(
            str(data["message"]),
            "{'email': ['Not a valid email address.'], 'password': ['Shorter than minimum length 8.']}",
        )
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 401)

        # Missing email and password.
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict("")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertEqual(
            str(data["message"]),
            "{'email': ['Email is required.'], 'password': ['Password is required.']}",
        )
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

    def test_login_registered_user(self):
        """Test POST /auth/login
        Login a registered user
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="crow@example.com", password="12345678")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["message"] == "Successfully registered.")
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/auth/login",
            data=json.dumps(dict(email="crow@example.com", password="12345678")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(data["message"], "Successfully logged in.")
        self.assertTrue(data["auth_token"])
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 200)

    def test_login_registered_user_wrong_password_fails(self):
        """Test POST /auth/login
        A registered user attempts to login with the wrong password
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="crownie@example.com", password="87654321")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/auth/login",
            data=json.dumps(dict(email="crownie@example.com", password="12345678")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertEqual(data["message"], "Sorry, email or password was incorrect.")
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 404)

    def test_login_registered_user_missing_required_data_fails(self):
        """Test POST /auth/login
        Login a registered user with missing required (email/password) data
        """
        user = User(email="crownie@example.com", password="87654321")
        self.db_session.add(user)
        self.db_session.commit()

        response = self.client.post(
            "/auth/login",
            data=json.dumps(dict(email="crownie@example.com")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertEqual(
            str(data["message"]), "{'password': ['Password is required.']}"
        )
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 500)

    def test_unregistered_user_login_fails(self):
        """Test POST /auth/login
        An unregistered user tries to login.
        """
        response = self.client.post(
            "/auth/login",
            data=json.dumps(dict(email="hawk@example.com", password="12345678")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "fail")
        self.assertEqual(data["message"], "User does not exist.")
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 404)

    def test_valid_logout(self):
        """Test POST /auth/logout
        A valid user tries to logout before token expires
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="crownie@example.com", password="87654321")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/auth/login",
            data=json.dumps(dict(email="crownie@example.com", password="87654321")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["auth_token"])

        response = self.client.post(
            "/auth/logout", headers=dict(Bearer=data["auth_token"])
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertTrue(data["message"] == "Successfully logged out.")
        self.assertEqual(response.status_code, 200)

    def test_logout_after_the_token_expires(self):
        """Test POST /auth/logout
        A valid user tries to logout after their token has expired
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="crownie@example.com", password="87654321")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/auth/login",
            data=json.dumps(dict(email="crownie@example.com", password="87654321")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["auth_token"])

        # Token expires
        time.sleep(6)
        response = self.client.post(
            "/auth/logout", headers=dict(Bearer=data["auth_token"])
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["message"] == "Signature has expired.")
        self.assertEqual(response.status_code, 401)

    def test_valid_user_unable_to_access_resource_with_blacklisted_token(self):
        """Test POST /auth/logout
        A valid user logouts and tries to access a resource using a blacklisted token
        """
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="crownie@example.com", password="87654321")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/auth/login",
            data=json.dumps(dict(email="crownie@example.com", password="87654321")),
            content_type="application/json",
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["auth_token"])
        token = data["auth_token"]

        # Token is blacklisted on logout
        response = self.client.post("/auth/logout", headers=dict(Bearer=token))
        data = json.loads(response.data.decode())
        self.assertTrue(data["status"] == "success")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            "/pets",
            headers=dict(Bearer=token),
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["message"], "Token blacklisted. Please log in again.")
