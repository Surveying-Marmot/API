import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)

IS_PROD = os.environ.get('IS_HEROKU', None)

# Select the config file based on the scenario
if not 'unittest' in sys.modules:
    if IS_PROD:
        print("Running using Heroku configuration")
        app.config.from_object('config_heroku')
    else:
        app.config.from_object('config')
else:
    app.config.from_object('config_test')

db = SQLAlchemy(app)
auth = HTTPBasicAuth()
api = Api(app)

CORS(app)

from app import models, users, guide, photo