from datetime import datetime
from functools import wraps

from flask import jsonify, make_response, render_template, request
from sqlalchemy.orm import sessionmaker
from swiftflame.models.models import Base, Pet, User
from swiftflame.schemas.schemas import PetSchema
from swiftflame.swiftflame import app, engine
from werkzeug.security import generate_password_hash

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
            return page_not_found("Sorry, resource not available.")
        else:
            return func(*args, **kwargs)

    return wrapper


##########
# Schemas
##########
pets_schema = PetSchema(many=True)
pet_schema = PetSchema()


############
# Endpoints
############
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/auth/register", methods=["POST"])
@ignore_endpoint
def register_user():
    data = request.get_json()
    # check if user already exists
    user = db_session.query(User).filter_by(email=data.get("email")).first()

    if not user:
        try:
            user = User(
                email=data.get("email"),
                password=generate_password_hash(data.get("password")),
                registered_on=datetime.utcnow(),
                admin=False,
            )
            db_session.add(user)
            db_session.commit()
            # generate the auth token
            auth_token = user.encode_auth_token(user.id, app.config)
            response_object = {
                "status": "success",
                "message": "Successfully registered.",
                "auth_token": auth_token,
            }
            return make_response(jsonify(response_object)), 201
        except Exception as exc:
            response_object = {
                "status": "fail",
                "message": "Some error occurred. Please try again.",
            }
            return make_response(jsonify(response_object)), 401
    else:
        response_object = {
            "status": "fail",
            "message": "User already exists. Please Log in.",
        }
        return make_response(jsonify(response_object)), 202


@app.route("/pets", methods=["GET"])
@ignore_endpoint
def pets():
    """Get pets details
    Get an array of all the pets
    ---
    consumes: ["application/json"]
    produces: ["application/json"]
    responses:
      200:
        description: A list of pets to be returned
    """
    pets = db_session.query(Pet).all()
    results = pets_schema.dump(pets)
    return {"pets": results}


@app.route("/pet/<int:pet_id>", methods=["GET"])
@ignore_endpoint
def pet(pet_id):
    """Get pet details
    Get a details for a pet
    ---
    parameters:
    - name: pet_id
      in: path
      type: string
      required: true
    produces: ["application/json"]
    responses:
      200:
        description: Pet details
      404:
        description: Pet does not exist
    """
    pet = db_session.query(Pet).filter_by(id=pet_id).first()
    if pet is None:
        return page_not_found("Sorry, Pet does not exist.")
    else:
        results = pet_schema.dump(pet)
        return results


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", message=error), 404
