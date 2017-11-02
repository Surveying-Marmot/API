import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)

# Select the config file based on the scenario
if not 'unittest' in sys.modules:
    app.config.from_object('config')
else:
    app.config.from_object('config_test')

db = SQLAlchemy(app)
auth = HTTPBasicAuth()
api = Api(app)

CORS(app)

from app import models, users, guide, photo