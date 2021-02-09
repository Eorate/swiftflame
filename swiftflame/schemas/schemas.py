from marshmallow import Schema, fields


class PetSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    date_of_birth = fields.Str()
    species = fields.Str()
    breed = fields.Str()
    sex = fields.Str()
    colour_and_identifying_marks = fields.Str()
