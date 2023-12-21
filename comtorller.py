from datetime import date
from flask import render_template, request
from sqlalchemy import and_
from models import Movie, Actor, MovieActor, Director, MovieDirector
from app import create_app

app = create_app()


@app.route('/movie')
def hello_world():  # put application's code here
    movies = Movie.query.all()

    for movie in movies:
        print("name" + movie.name)

    return render_template('base.html')


# @app.route('/')
@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    Movie.name = request.form.get("name")
    Movie.actors = request.form.get("actor")
    Movie.directors = request.form.get('director')
    Movie.country = request.form.get("country")
    Movie.release_date = request.form.get("startDate") or date(1700, 1, 31)

    Movie.type = request.form.get("film_format")
    Movie.company = request.form.get("company")
    Movie.box = request.form.get("box")
    Movie.film_format = request.form.get("film_format")

    print(Movie.name, Movie.actors, Movie.directors, Movie.country, Movie.release_date, Movie.type, Movie.company,
          Movie.box, Movie.film_format)

    return


@app.route('/query_movies', methods=['GET', 'POST'])
def query_movies():
    # 读取表单数据
    movieIdDirectors = ''
    directorsIds = ''
    actorIds = ''
    movieIdActors = ''
    name = request.form.get("name")
    actor = request.form.get("actor")
    director = request.form.get('director')
    country = request.form.get("country")
    start_date = request.form.get("startDate") or date(1700, 1, 31)
    end_date = request.form.get("endDate") or date(9999, 12, 31)
    type = request.form.get("film_format")
    company = request.form.get("company")
    start_box = request.form.get("start_box") or 0
    end_box = request.form.get("end_box") or 999999999999

    # ac = Actor.query.filter(Actor.name.like(actor))
    # print(name, actor, country, start_date, end_date, type, company, start_box, end_box)
    # 执行查询

    results = Movie.query.filter(and_(Movie.name.like(f'%{name}%'),
                                      Movie.country.like(f'%{country}%'),
                                      Movie.release_date > start_date,
                                      Movie.release_date < end_date,
                                      Movie.type.like(f'%{type}'),
                                      Movie.company.like(f'%{company}%'),
                                      Movie.box >= start_box,
                                      Movie.box <= end_box
                                      ))
    if actor:
        actors = Actor.query.filter(Actor.name.like(f'%{actor}%')).all()
        print(actors)
        for actor in actors:
            actorIds = str(actor.id) + ',' + actorIds
        actorIds = actorIds.split(',')

        movie_actors = MovieActor.query.filter(MovieActor.actor_id in actorIds)

        for movieActor in movie_actors:
            movieIdActors = str(movieActor.movie_id) + ',' + movieIdActors
        movieIdActors = movieIdActors.split(',')
        results.filter(Movie.id in movieIdActors)

    if director:
        directors = Director.query.filter(Director.name.like(f'%{director}%'))
        for director in directors:
            directorsIds = str(director.id) + ',' + directorsIds
        directorsIds = directorsIds.split(',')

        movie_directors = MovieDirector.query.filter(MovieDirector.movie_id in directorsIds)

        for movieDirector in movie_directors:
            movieIdDirectors = str(movieDirector.id) + ',' + movieIdDirectors
        movieIdDirectors = movieIdDirectors.split(',')
        results.filter(Movie.id in movieIdDirectors)
    return render_template('query_movies.html', movies=results.all())
