from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'lololol'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kk.db'
    
    db.init_app(app)

    from .page import page
    app.register_blueprint(page, url_prefix='/')

    from . import database

    return app