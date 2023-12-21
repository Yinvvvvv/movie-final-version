from datetime import date

import pandas as pd
from flask import render_template, request, flash
from sqlalchemy import and_, func, delete
import plotly.express as px
from extensions import db
from models import Movie, Actor, MovieActor, Director, MovieDirector
from app import create_app

app = create_app()


@app.route('/')
def first():  # put application's code here

    return render_template('base.html')


@app.route('/query_actor', methods=['GET', 'POST'])
def query_actor():  # put application's code here
    # print(request.form)
    # 读取表单数据
    movieIdDirectors = ''
    directorsIds = ''
    movieIdActors = ''
    actor = request.form.get("actor")

    actors = Actor.query.filter(Actor.name.like(f'%{actor}%')).all()
    actorIds = []
    for actor in actors:
        actorIds.append(str(actor.id))
    movie_actors = MovieActor.query.filter(MovieActor.actor_id.in_(actorIds)).all()

    for movieActor in movie_actors:
        movieIdActors = str(movieActor.movie_id) + ',' + movieIdActors
    movieIdActors = movieIdActors.split(',')
    results = Movie.query.filter(Movie.id.in_(movieIdActors))

    director = request.form.get('director')
    directors = Director.query.filter(Director.name.like(f'%{director}%'))
    directorIds = []
    for director in directors:
        directorIds.append(director.id)

    movie_directors = MovieDirector.query.filter(MovieDirector.director_id.in_(directorIds)).all()

    for movieDirector in movie_directors:
        movieIdDirectors = str(movieDirector.movie_id) + ',' + movieIdDirectors
    movieIdDirectors = movieIdDirectors.split(',')
    results.filter(Movie.id.in_(movieIdDirectors)).all()

    results = Movie.query.filter(and_(Movie.id.in_(movieIdActors)
                                      , Movie.id.in_(movieIdDirectors
                                                     ))).all()

    # director

    for movie in results:
        # 初始化导演ID列表
        directorids = []

        # 查询与当前电影相关联的所有导演
        MovieDirectors = MovieDirector.query.filter(MovieDirector.movie_id == movie.id).all()
        directorids.extend([str(movieDirector.director_id) for movieDirector in MovieDirectors])

        # 初始化导演名字字符串
        names = ''

        # 查询导演ID对应的导演信息
        directors = Director.query.filter(Director.id.in_(directorids)).all()

        # 构建包含所有导演名字的字符串
        for director in directors:
            names = director.name + ',' + names

        # 更新电影对象的导演属性
        movie.directors = names.rstrip(',')  # 移除字符串末尾的逗号

    # actor

    for movie in results:
        actorids = []
        MovieActors = MovieActor.query.filter(MovieActor.movie_id == movie.id).all()
        actorids.extend([str(movieActor.actor_id) for movieActor in MovieActors])
        actors = Actor.query.filter(Actor.id.in_(actorids)).all()

        # 创建演员名单字符串
        names = ', '.join([actor.name for actor in actors])
        movie.actors = names

    return render_template('query_actor.html', movies=results)


# @app.route('/')
@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    name = request.form.get("name")
    country = request.form.get("country")
    release_date = request.form.get("release_date")
    type = request.form.get("type")
    company = request.form.get("company")
    box = request.form.get("box")
    film_format = request.form.get("film_format")

    try:

        new_movie = Movie(name=name, country=country, release_date=release_date, type=type, company=company, box=box,
                          film_format=film_format)
        db.session.add(new_movie)
        # db.session.commit()

        newMovie = Movie.query.filter(Movie.name == name).first()
        movie_ID = newMovie.id

        from_actornames = request.form.get("actor"),
        actornames = str(from_actornames).split(',')

        for actorname in actornames:
            actors = Actor.query.filter(Actor.name == actorname).first()
            if actors is None:
                new_actor = Actor(name=actorname)
                db.session.add(new_actor)
                # db.session.commit()
            actors = Actor.query.filter(Actor.name == actorname).first()

            new_movie_actor = MovieActor(movie_id=movie_ID, actor_id=actors.id)
            db.session.add(new_movie_actor)
            # db.session.commit()

        from_directors = request.form.get('director')
        director_names = str(from_directors).split(',')
        for director_name in director_names:
            director = Director.query.filter(Director.name == director_name).first()
            if director is None:
                new_director = Director(name=director_name)
                db.session.add(new_director)
                # db.session.commit()
            director = Director.query.filter(Director.name == director_name).first()

            new_movie_director = MovieDirector(movie_id=movie_ID, director_id=director.id)
            db.session.add(new_movie_director)
        db.session.commit()
        flash('电影添加成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'电影添加失败', 'error')

    return render_template('query_movies.html')


@app.route('/data', methods=['GET', 'POST'])
def data():
    ids = request.form.getlist('ids')
    option = request.form.get('option')
    if option == 'country':
        df_data = [
            {"country": movie[0], "total_box": movie[1]}
            for movie in
            db.session.query(Movie.country, func.sum(Movie.box)).group_by(Movie.country).filter(Movie.id.in_(ids)).all()
        ]
        df = pd.DataFrame(df_data)
        fig = px.bar(df, x='country', y='total_box', title='movie')
    if option == 'release_date':
        df_data = [{column.name: getattr(movie, column.name) for column in Movie.__table__.columns} for movie in
                   Movie.query.order_by(Movie.release_date).filter(Movie.id.in_(ids)).all()]
        df = pd.DataFrame(df_data)

        fig = px.line(df, x='release_date', y='box', title='movie')
    if option == 'type':
        df_data = [
            {"type": movie[0], "total_box": movie[1]}
            for movie in
            db.session.query(Movie.type, func.sum(Movie.box)).group_by(Movie.type).filter(Movie.id.in_(ids)).all()
        ]
        df = pd.DataFrame(df_data)
        fig = px.bar(df, x='type', y='total_box', title='movie')
    if option == 'film_format':
        df_data = [
            {"film_format": movie[0], "total_box": movie[1]}
            for movie in db.session.query(Movie.film_format, func.sum(Movie.box)).group_by(Movie.film_format).filter(
                Movie.id.in_(ids)).all()
        ]
        df = pd.DataFrame(df_data)
        print(df.columns.all())
        fig = px.bar(df, x='film_format', y='total_box', title='movie')

    graph_html = fig.to_html(full_html=False)
    return render_template('data.html', plotly_chart=graph_html)


@app.route('/query_movies', methods=['GET', 'POST'])
def query_movies():
    # 读取表单数据

    name = request.form.get("name")

    country = request.form.get("country")
    start_date = request.form.get("startDate") or date(1700, 1, 31)
    end_date = request.form.get("endDate") or date(9999, 12, 31)
    type = request.form.get("type")

    start_box = request.form.get("start_box") or 0
    end_box = request.form.get("end_box") or 999999999999

    # 执行查询

    results = Movie.query.filter(and_(Movie.name.like(f'%{name}%'),
                                      Movie.country.like(f'%{country}%'),
                                      Movie.release_date > start_date,
                                      Movie.release_date < end_date,
                                      Movie.type.like(f'%{type}'),
                                      Movie.box >= start_box,
                                      Movie.box <= end_box
                                      ))
    return render_template('query_movies.html', movies=results.all())


@app.route('/movie_data', methods=['GET', 'POST'])
def movie_data():
    # 读取表单数据

    name = request.form.get("name")

    country = request.form.get("country")
    start_date = request.form.get("startDate") or date(1700, 1, 31)
    end_date = request.form.get("endDate") or date(9999, 12, 31)
    type = request.form.get("type")

    start_box = request.form.get("start_box") or 0
    end_box = request.form.get("end_box") or 999999999999

    # 执行查询

    results = Movie.query.filter(and_(Movie.name.like(f'%{name}%'),
                                      Movie.country.like(f'%{country}%'),
                                      Movie.release_date > start_date,
                                      Movie.release_date < end_date,
                                      Movie.type.like(f'%{type}'),
                                      Movie.box >= start_box,
                                      Movie.box <= end_box
                                      ))
    return render_template('movie_data.html', movies=results.all())


@app.route('/edit_page/<int:movie_id>', methods=['GET', 'POST'])
def edit_page(movie_id):
    movie = Movie.query.filter(Movie.id == movie_id).first()

    # 初始化导演ID列表
    directorids = []

    # 查询与当前电影相关联的所有导演
    MovieDirectors = MovieDirector.query.filter(MovieDirector.movie_id == movie.id).all()
    directorids.extend([str(movieDirector.director_id) for movieDirector in MovieDirectors])

    # 初始化导演名字字符串
    names = ''

    # 查询导演ID对应的导演信息
    directors = Director.query.filter(Director.id.in_(directorids)).all()

    # 构建包含所有导演名字的字符串
    for director in directors:
        names = director.name + ',' + names

    # 更新电影对象的导演属性
    movie.directors = names.rstrip(',')  # 移除字符串末尾的逗号

    # actor

    actorids = []
    MovieActors = MovieActor.query.filter(MovieActor.movie_id == movie.id).all()
    actorids.extend([str(movieActor.actor_id) for movieActor in MovieActors])
    actors = Actor.query.filter(Actor.id.in_(actorids)).all()

    # 创建演员名单字符串
    names = ', '.join([actor.name for actor in actors])
    movie.actors = names

    return render_template('edit_movie.html', movie=movie)


@app.route('/edit_movie/', methods=['GET', 'POST'])
def edit_movie():
    try:
        new_movie = request.form
        movie = Movie.query.filter(Movie.id == new_movie.get('id')).first()
        movie.name = new_movie.get('name')
        movie.release_date = new_movie.get('release_date')
        movie.type = new_movie.get('type')
        movie.box = new_movie.get('box')
        movie.country = new_movie.get('country')
        movie.actors=new_movie.get('old_actors')
        movie.directors=new_movie.get('old_directors')

        # actor
        if movie.actors != new_movie.get('actors'):
            # 查询出要删除的记录
            movie_actors_to_delete = MovieActor.query.filter(MovieActor.movie_id == movie.id).all()
            # 遍历并删除每条记录
            for actor in movie_actors_to_delete:
                db.session.delete(actor)
            names = new_movie.get('actors')
            names = names.split(',')
            for name in names:
                actor = Actor.query.filter(Actor.name == name).first()
                if actor is None:
                    new_actor = Actor(name=name)
                    db.session.add(new_actor)
                actor = Actor.query.filter(Actor.name == name).first()
                new_movie_actor=MovieActor(movie_id=movie.id,actor_id=actor.id)
                db.session.add(new_movie_actor)
            # directors
        if movie.directors != new_movie.get('directors'):
            # 查询出要删除的记录
            movie_directors_to_delete = MovieDirector.query.filter(MovieDirector.movie_id == movie.id).all()
            # 遍历并删除每条记录
            for director in movie_directors_to_delete:
                db.session.delete(director)
            names=new_movie.get('directors')
            names=names.split(',')
            for name in names:
                director = Director.query.filter(Director.name==name)
                if director is None:
                    new_director = Director(name=name)
                    db.session.add(new_director)
                director = Director.query.filter(Director.name==name).first()
                new_movie_director=MovieDirector(movie_id=movie.id,director_id=director.id)
                db.session.add(new_movie_director)

        db.session.commit()
        flash('movie update success！', 'success')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('movie update error','error')

    return render_template('query_movies.html')


@app.route('/delete_movie/<int:movie_id>', methods=['GET', 'POST'])
def delete_movie(movie_id):
    try:
        delete_movie = Movie.query.filter(Movie.id == movie_id).all()
        delete_movie_actors = MovieActor.query.filter(MovieActor.movie_id == movie_id).all()
        delete_movie_directors = MovieDirector.query.filter(MovieDirector.movie_id == movie_id).all()

        for actor in delete_movie_actors:
            db.session.delete(actor)

            # Delete movie directors
        for director in delete_movie_directors:
            db.session.delete(director)

            # Delete the movie
        for movie in delete_movie:
            db.session.delete(movie)
        flash('movie delete success！', 'success')
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('movie delete error', 'error')
    return render_template('query_movies.html')
