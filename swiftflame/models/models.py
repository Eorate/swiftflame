from sqlalchemy import Column, Date, Integer, String, Text
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
