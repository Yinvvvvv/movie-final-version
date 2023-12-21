from sqlalchemy.util.preloaded import orm

from app import db


class Movie(db.Model):
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    country = db.Column(db.String(30))
    release_date = db.Column(db.Date)
    type = db.Column(db.String(20))
    film_format = db.Column(db.String(50))
    company = db.Column(db.String(1000))
    box = db.Column(db.BigInteger)
    # actors =
    # directors = str
    actors = db.Column(db.String(5000))
    directors = db.Column(db.String(2000))
    # actors = db.relationship('Actor', secondary='movie_actor', back_populates='movies')
    # directors = db.relationship('Director', secondary='movie_director', back_populates='movies')


class Director(db.Model):
    __tablename__ = 'director'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    # movies = db.relationship('Movie', secondary='movie_director', back_populates='directors')


class Actor(db.Model):
    __tablename__ = 'actor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # movies = db.relationship('Movie', secondary='movie_actor', back_populates='actors')


class MovieActor(db.Model):
    __tablename__ = 'movie_actor'

    movie_id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, primary_key=True)


class MovieDirector(db.Model):
    __tablename__ = 'movie_director'

    movie_id = db.Column(db.Integer, primary_key=True)
    director_id = db.Column(db.Integer, primary_key=True)
