from datetime import datetime, timedelta

import jwt
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date(), nullable=False)
    species = Column(String(10), nullable=False)
    breed = Column(String(20), nullable=False)
    sex = Column(String(1), nullable=False)
    colour_and_identifying_marks = Column(String(200), nullable=False)
    photo = Column(Text, nullable=True, default="default.png")

    def __repr__(self):
        return (
            "<Pet\nid: {}\nname: {}\ndate_of_birth: {}\nspecies: {}\nbreed: {}\n"
            "sex: {}\ncolour_and_identifying_marks: {}\nphoto: {}\n>"
        ).format(
            self.id,
            self.name,
            self.date_of_birth,
            self.species,
            self.breed,
            self.sex,
            self.colour_and_identifying_marks,
            self.photo,
        )


class User(Base):
    __tablename__ = "site_users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    registered_on = Column(DateTime, default=datetime.utcnow())
    admin = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<User email={}, admin={}>".format(self.email, self.admin)

    def encode_auth_token(self, user_id, config):
        """
        Generates the Auth Token

        Keyword arguments:
        user_id - user id
        config - application configuration

        Returns a string
        """
        token_expire_hours = config.get("TOKEN_EXPIRE_HOURS")
        token_expire_minutes = config.get("TOKEN_EXPIRE_MINUTES")
        expire = (
            datetime.utcnow()
            + timedelta(hours=token_expire_hours, minutes=token_expire_minutes),
        )
        if config["TESTING"]:
            token_expire_seconds = config.get("TOKEN_EXPIRE_SECONDS")
            expire = datetime.utcnow() + timedelta(seconds=token_expire_seconds)
        payload = {
            "exp": expire,
            "iat": datetime.utcnow(),
            "sub": self.id,
            "admin": self.admin,
        }
        return jwt.encode(payload, config.get("SECRET_KEY"), algorithm="HS256")
