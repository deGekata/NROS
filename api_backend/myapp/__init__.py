"""Flask app initializer"""
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from config import Config



app = Flask(__name__) # pylint: disable=invalid-name
app.config.from_object(Config)
api = Api(app) # pylint: disable=invalid-name
db = SQLAlchemy(app) # pylint: disable=invalid-name

from myapp.models import * # pylint: disable=wrong-import-position

migrate = Migrate(app, db) # pylint: disable=invalid-name
CORS(app)

from myapp import api_routes # pylint: disable=wrong-import-position
