import json
import time
import unittest
from datetime import date

from swiftflame.models.models import Pet, User
from swiftflame.swiftflame import app
from swiftflame.views.main import db_session


class TestCaseEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.db_session = db_session
        self.db_session.query(Pet).delete()
        self.db_session.query(User).delete()
        self.db_session.commit()
        self.hero = Pet(
            name="Hero",
            date_of_birth=date(2020, 8, 1),
            species="Canine",
            sex="M",
            breed="Rotweiller",
            colour_and_identifying_marks="Black and Brown",
            photo="default.png",
        )
        self.db_session.add(self.hero)
        self.mayhem = Pet(
            name="Mayhem",
            date_of_birth=date(2019, 4, 1),
            species="Canine",
            sex="M",
            breed="Bulldog",
            colour_and_identifying_marks="Brown",
            photo="default.png",
        )
        self.db_session.add(self.mayhem)
        self.db_session.commit()

    def register_user(self):
        response = self.client.post(
            "/auth/register",
            data=json.dumps(dict(email="scrapy@example.com", password="scrapy123456")),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        return json.loads(response.data.decode())["auth_token"]

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_get_pets(self):
        """Test GET /pets"""
        auth_token = self.register_user()
        response = self.client.get("/pets", headers=dict(Bearer=auth_token))

        self.assertEqual(response.status_code, 200)
        expected_pets = {
            "pets": [
                {
                    "breed": "Rotweiller",
                    "colour_and_identifying_marks": "Black and Brown",
                    "date_of_birth": "2020-08-01",
                    "id": self.hero.id,
                    "name": "Hero",
                    "sex": "M",
                    "species": "Canine",
                },
                {
                    "breed": "Bulldog",
                    "colour_and_identifying_marks": "Brown",
                    "date_of_birth": "2019-04-01",
                    "id": self.mayhem.id,
                    "name": "Mayhem",
                    "sex": "M",
                    "species": "Canine",
                },
            ]
        }
        self.assertEqual(response.get_json(), expected_pets)

    def test_get_pets_when_none_exist(self):
        "Test GET /pets on empty database"
        self.db_session.query(Pet).delete()
        self.db_session.commit()

        auth_token = self.register_user()
        response = self.client.get("/pets", headers=dict(Bearer=auth_token))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"pets": []})

    def test_get_pets_when_no_token_is_provided(self):
        "Test GET /pets but no token provided in header"
        response = self.client.get(
            "/pets",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"message": "A valid token is missing."})

    def test_get_pets_when_token_can_not_be_decoded(self):
        "Test GET /pets but token provided is not JWT and can not be decoded"
        response = self.client.get(
            "/pets",
            headers=dict(Bearer="some-random-strings"),
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"message": "Token is invalid."})

    def test_get_pets_when_token_signature_has_expired(self):
        "Test GET /pets but token used has expired"
        auth_token = self.register_user()

        # Let's wait for the token to expire
        time.sleep(6)

        response = self.client.get(
            "/pets",
            headers=dict(Bearer=auth_token),
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"message": "Signature has expired."})

    def test_get_pets_when_token_is_invalid(self):
        "Test GET /pets but token is not valid"
        auth_token = self.register_user()
        response = self.client.get("/pets", headers=dict(Bearer=auth_token[:-1]))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(), {"message": "Signature verification failed."}
        )

    def test_get_pet_given_id(self):
        """Test GET /pet/id"""
        auth_token = self.register_user()
        response = self.client.get(
            "/pet/{}".format(self.hero.id),
            headers=dict(Bearer=auth_token),
        )
        self.assertEqual(response.status_code, 200)
        expected_pet = {
            "breed": "Rotweiller",
            "colour_and_identifying_marks": "Black and Brown",
            "date_of_birth": "2020-08-01",
            "id": self.hero.id,
            "name": "Hero",
            "sex": "M",
            "species": "Canine",
        }
        self.assertEqual(response.get_json(), expected_pet)

    def test_get_pet_given_unknown_pet_id(self):
        """Test GET /pet/id"""
        auth_token = self.register_user()
        response = self.client.get(
            "/pet/{}".format(0),
            headers=dict(Bearer=auth_token),
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json(),
            {"message": "Sorry, Pet does not exist.", "status": "fail"},
        )
