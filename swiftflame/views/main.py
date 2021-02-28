from flask import render_template
from sqlalchemy.orm import sessionmaker
from swiftflame.models.models import Base, Pet
from swiftflame.schemas.schemas import PetSchema
from swiftflame.swiftflame import app, engine
from functools import wraps

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


############
# Endpoints
############
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/pets", methods=["GET"])
@ignore_endpoint
def pets():
    pets = db_session.query(Pet).all()
    results = pets_schema.dump(pets)
    return {"pets": results}


@app.errorhandler(404)
def page_not_found(error):
        return render_template("404.html", message=error), 404
