import os


class Config(object):
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    IGNORE_ENDPOINTS = False
    TOKEN_EXPIRE_HOURS = 1
    TOKEN_EXPIRE_MINUTES = 0
    TOKEN_EXPIRE_SECONDS = 0
    SWAGGER = {
        "title": "PetsRUsAPI",
        "description": "API for PetsRUs",
        "uiversion": 3,
        "consumes": [
            "application/json",
        ],
        "produces": [
            "application/json",
        ],
    }


class ProductionConfig(Config):
    DEBUG = os.environ.get("DEBUG", default=False)
    if str(DEBUG).lower() in ("f", "false"):
        DEBUG = False

    SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", default=None)
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No database url provided for Flask application")

    # Endpoints under development are kept hidden to clients by this flag
    # Yes -- returns an error message
    IGNORE_ENDPOINTS = os.environ.get("IGNORE_ENDPOINTS", default="Yes")
    if str(IGNORE_ENDPOINTS).lower() in ("y", "yes"):
        IGNORE_ENDPOINTS = True
    elif str(IGNORE_ENDPOINTS).lower() in ("n", "no"):
        IGNORE_ENDPOINTS = False


class DevelopmentConfig(Config):
    DEBUG = os.environ.get("DEBUG", default=False)
    if str(DEBUG).lower() in ("f", "false"):
        DEBUG = False

    SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", default=None)
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No database url provided for Flask application")

    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS", default=False
    )

    IGNORE_ENDPOINTS = os.environ.get("IGNORE_ENDPOINTS", default="Yes")
    if str(IGNORE_ENDPOINTS).lower() in ("y", "yes"):
        IGNORE_ENDPOINTS = True
    elif str(IGNORE_ENDPOINTS).lower() in ("n", "no"):
        IGNORE_ENDPOINTS = False


class TestingConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", default=None)
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No database url provided for Flask application")

    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS", default=False
    )

    TESTING = os.environ.get("TESTING", default=True)
    TOKEN_EXPIRE_HOURS = os.environ.get("TOKEN_EXPIRE_HOURS", default=0)
    TOKEN_EXPIRE_MINUTES = os.environ.get("TOKEN_EXPIRE_MINUTES", default=0)
    TOKEN_EXPIRE_SECONDS = os.environ.get("TOKEN_EXPIRE_SECONDS", default=5)

    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False
    LOGIN_DISABLED = True
