import os

from flasgger import Swagger
from flask import Flask
from sqlalchemy import create_engine

app = Flask(__name__)
app.config.from_object(
    os.environ.get("APP_SETTINGS", default="config.DevelopmentConfig")
)
swagger = Swagger(app)

# Create an engine that stores data in the env database
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])


from swiftflame.views import main  # noqa isort:skip
