from flask import Flask
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = r"mysql://root:123456@localhost:3306/moviedb"
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config['SQLALCHEMY_DATABASE_CHARSET'] = 'utf8'
    app.debug = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    db.init_app(app)

    return app


#     导入路由
from comtorller import *
