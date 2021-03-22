import unittest
from datetime import date

from swiftflame.models.models import Pet
from swiftflame.swiftflame import app
from swiftflame.views.main import db_session


class TestCaseEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        self.db_session = db_session
        self.db_session.query(Pet).delete()
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

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_get_pets(self):
        """Test GET /pets"""
        response = self.client.get("/pets")
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
