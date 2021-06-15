import traceback
from functools import wraps

import jwt
from flask import jsonify, make_response, render_template, request
from marshmallow import ValidationError
from sqlalchemy.orm import sessionmaker
from swiftflame.models.models import Base, Pet, User
from swiftflame.schemas.schemas import PetSchema, UserSchema
from swiftflame.swiftflame import app, engine
from werkzeug.security import check_password_hash

Base.metadata.bind = engine
Base.metadata.create_all()
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


#######################
# Toggle off endpoints
#######################
def ignore_endpoint(func):
    """Ignore Endpoint allows us to toggle whether an endpoint is
    available or not"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if app.config["IGNORE_ENDPOINTS"]:
            return not_found("Sorry, resource not available.")
        else:
            return func(*args, **kwargs)

    return wrapper


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if "Bearer" in request.headers:
            token = request.headers["Bearer"]

        if not token:
            response = {"message": "A valid token is missing."}
            app.logger.error("response: {}| status_code: {}".format(response, 401))
            return make_response(jsonify(response)), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
            current_user = db_session.query(User).filter_by(id=data["sub"]).first()
        except jwt.exceptions.InvalidSignatureError as exc:
            app.logger.error(exc)
            return (
                make_response(jsonify({"message": "Signature verification failed."})),
                401,
            )
        except jwt.exceptions.ExpiredSignatureError as exc:
            # TODO: We need to return the following as per the spec
            # HTTP/1.1 401 Unauthorized
            # WWW-Authenticate: Bearer realm="example",
            #                   error="invalid_token",
            #                   error_description="The access token expired"
            app.logger.error(exc)
            return make_response(jsonify({"message": "Signature has expired."})), 401
        except jwt.exceptions.InvalidTokenError as exc:
            app.logger.error(traceback.format_exc())
            return make_response(jsonify({"message": "Token is invalid."})), 401
        return f(current_user, *args, **kwargs)

    return decorator


##########
# Schemas
##########
pets_schema = PetSchema(many=True)
pet_schema = PetSchema()
user_schema = UserSchema()


############
# Endpoints
############
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/auth/register", methods=["POST"])
@ignore_endpoint
def register_user():
    """Register users
    Register new users
    ---
    parameters:
      - in: body
        name: body
        description: JSON parameters.
        schema:
          properties:
            email:
              type: string
              description: email address.
              example: milo@example.com
            password:
              type: string
              description: Password.
              example: mysecretpassword
    responses:
      201:
        description: Successfully registered.
      202:
        description: User already exists. Please login.
      401:
        description: Some error occured. Please try again.
    """
    data = request.get_json()
    # check if user already exists
    user = db_session.query(User).filter_by(email=data.get("email")).first()

    if not user:
        try:
            user = user_schema.load(data)
            db_session.add(user)
            db_session.commit()
            # generate the auth token
            auth_token = user.encode_auth_token(user.id, app.config)
            response_object = {
                "status": "success",
                "message": "Successfully registered.",
                "auth_token": auth_token,
            }
            app.logger.info(
                "message: {}| status: {}| status_code: {}".format(
                    response_object["message"], response_object["status"], 201
                )
            )
            return make_response(jsonify(response_object)), 201
        except ValidationError as err:
            response_object = {
                "status": "fail",
                "message": err.messages,
            }
            app.logger.error(
                "message: {}| status: {}| status_code: {}".format(
                    response_object["message"], response_object["status"], 401
                )
            )
            return make_response(jsonify(response_object)), 401
    else:
        response_object = {
            "status": "fail",
            "message": "User already exists. Please Log in.",
        }
        app.logger.error(
            "message: {}| status: {}| status_code: {}".format(
                response_object["message"], response_object["status"], 202
            )
        )
        return make_response(jsonify(response_object)), 202


@app.route("/auth/login", methods=["POST"])
@ignore_endpoint
def login_user():
    """Login users
    Login registered users
    ---
    parameters:
      - in: body
        name: body
        description: JSON parameters.
        schema:
          properties:
            email:
              type: string
              description: email address.
              example: milo@example.com
            password:
              type: string
              description: Password.
              example: mysecretpassword
    responses:
      200:
        description: Successfully logged in.
      404:
        description: User does not exist or
          Email/Password provided was incorrect.
      500:
        description: Some error occured. Please try again.
    """
    post_data = request.get_json()
    try:
        post_user = user_schema.load(post_data)

        user = db_session.query(User).filter_by(email=post_user.email).first()

        if user and check_password_hash(user.password, post_data.get("password")):
            auth_token = user.encode_auth_token(user.id, app.config)
            response_object = {
                "status": "success",
                "message": "Successfully logged in.",
                "auth_token": auth_token,
            }
            app.logger.info(
                "message: {}| status: {}| status_code: {}".format(
                    response_object["message"], response_object["status"], 200
                )
            )
            return make_response(jsonify(response_object)), 200
        elif not user:
            response_object = {
                "status": "fail",
                "message": "User does not exist.",
            }
            app.logger.error(
                "message: {}| status: {}| status_code: {}".format(
                    response_object["message"], response_object["status"], 404
                )
            )
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                "status": "fail",
                "message": "Sorry, email or password was incorrect.",
            }
            app.logger.error(
                "message: {}| status: {}| status_code: {}".format(
                    response_object["message"], response_object["status"], 404
                )
            )
            return make_response(jsonify(response_object)), 404
    except ValidationError as err:
        response_object = {
            "status": "fail",
            "message": err.messages,
        }
        app.logger.error(
            "message: {}| status: {}| status_code: {}".format(
                response_object["message"], response_object["status"], 500
            )
        )
        return make_response(jsonify(response_object)), 500


@app.route("/pets", methods=["GET"])
@ignore_endpoint
@token_required
def pets(current_user):
    """Get pets details
    Get an array of all the pets
    ---
    security:
       - Bearer: []
    responses:
      200:
        description: A list of pets to be returned
      401:
        description: Invalid Token errors
    """
    # You should return the pets that belong to the client.
    # So now we have to deal with teams or something close to that.
    pets = db_session.query(Pet).all()
    results = pets_schema.dump(pets)
    return make_response(jsonify({"pets": results})), 200


@app.route("/pet/<int:pet_id>", methods=["GET"])
@ignore_endpoint
@token_required
def pet(current_user, pet_id):
    """Get pet details
    Get a details for a given pet
    ---
    parameters:
    - name: pet_id
      in: path
      type: string
      required: true
    security:
       - Bearer: []
    responses:
      200:
        description: Pet details
      401:
        description: Invalid Token errors
      404:
        description: Pet does not exist
    """
    pet = db_session.query(Pet).filter_by(id=pet_id).first()
    if pet is None:
        return not_found("Sorry, Pet does not exist.")
    else:
        results = pet_schema.dump(pet)
        return results


def not_found(error):
    response_object = {
        "status": "fail",
        "message": error,
    }
    app.logger.error(
        "message: {}| status: {}| status_code: {}".format(
            response_object["message"], response_object["status"], 404
        )
    )
    return make_response(jsonify(response_object)), 404
