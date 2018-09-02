import os

DEBUG = True
SECRET_KEY = os.urandom(24)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:lixn@127.0.0.1:3306/msite'
UP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)))
REDIS_URL = "redis://127.0.0.1:6379/0"