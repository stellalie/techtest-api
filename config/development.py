import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEVELOPMENT = True
DEBUG = True
SECRET_KEY = 'this-really-needs-to-be-changed'
SQLALCHEMY_DATABASE_URI = 'sqlite:///../resources/db.sqlite3'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO=True
