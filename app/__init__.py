from flask import Flask
from . import config
from flask_sqlalchemy import SQLAlchemy

mainapp = Flask(__name__)
mainapp.config.from_object(config)
db = SQLAlchemy(mainapp)

from .admin import admin
from .home import home
mainapp.register_blueprint(home)
mainapp.register_blueprint(admin,url_prefix="/admin")

