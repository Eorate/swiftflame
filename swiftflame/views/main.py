from flask import render_template
from sqlalchemy.orm import sessionmaker
from swiftflame.models.models import Base, Pet
from swiftflame.schemas.schemas import PetSchema
from swiftflame.swiftflame import app, engine

Base.metadata.bind = engine
Base.metadata.create_all()
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


pets_schema = PetSchema(many=True)


@app.route("/pets", methods=["GET"])
def pets():
    pets = db_session.query(Pet).all()
    results = pets_schema.dump(pets)
    return {"pets": results}
