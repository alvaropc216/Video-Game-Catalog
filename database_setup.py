from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False, unique = True)
    id = Column(Integer,primary_key = True)
    picture = Column(String(250))

class Genre(Base):
    __tablename__ = 'genre'
    name = Column(String(80), nullable = False)
    count = Column(Integer)
    id = Column(Integer,primary_key = True)
    user_id = Column(Integer,ForeignKey('user.id'))
    users=relationship(User)

    @property
    def serialize(self):
        return {
        'name' : self.name,
        'count' : self.count,
        'id' : self.id,
        'user_id': self.user_id,
        }


class Game(Base):
    __tablename__='game'
    name = Column(String(250),nullable = False,unique = True)
    id = Column(Integer,primary_key = True)
    id_genre = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)
    description = Column(String(300))
    user_id = Column(Integer,ForeignKey('user.id'))
    users=relationship(User)

    @property
    def serialize(self):
        return {
        'name' : self.name,
        'id' : self.id,
        'id_genre':self.id_genre,
        'description' : self.description,
        'user_id' : self.user_id,
        }

engine = create_engine('sqlite:///gamecatalog.db')

Base.metadata.create_all(engine)
