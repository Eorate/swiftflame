from flask import Flask
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

from swiftflame.views import main  # noqa isort:skip
