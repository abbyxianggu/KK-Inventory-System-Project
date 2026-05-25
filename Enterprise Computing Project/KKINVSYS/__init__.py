from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'lololol'
    
    from .page import page
    app.register_blueprint(page, url_prefix='/')

    return app