from datetime import datetime

from marshmallow import Schema, fields, post_load, validate
from swiftflame.models.models import User
from werkzeug.security import generate_password_hash


class PetSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    date_of_birth = fields.Str()
    species = fields.Str()
    breed = fields.Str()
    sex = fields.Str()
    colour_and_identifying_marks = fields.Str()


class UserSchema(Schema):
    id = fields.Str()
    email = fields.Email(
        required=True, error_messages={"required": "Email is required."}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={"required": "Password is required."},
    )
    registered_on = fields.DateTime(default=datetime.utcnow())
    admin = fields.Str(default=False)

    @post_load
    def make_object(self, data, **kwargs):
        if not data:
            return None
        return User(
            email=data["email"],
            password=generate_password_hash(data["password"]),
        )
