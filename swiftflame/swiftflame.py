import os

from flasgger import Swagger
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import create_engine

csrf = CSRFProtect()
app = Flask(__name__)
app.config.from_object(
    os.environ.get("APP_SETTINGS", default="config.DevelopmentConfig")
)
swagger = Swagger(app)
csrf.init_app(app)

# Create an engine that stores data in the env database
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])


from swiftflame.views import main  # noqa isort:skip
