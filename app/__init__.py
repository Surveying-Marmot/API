from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
api = Api(app)

CORS(app)

from app import models, users, guide, photo