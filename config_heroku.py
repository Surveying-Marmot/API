"""
    Defines a set a config variables for testing the application
"""

import os

DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DIR, 'test.db')

BASE_URL = '/api/v1'

API_SECRET_KEY = os.environ.get('API_SECRET_KEY', None)

JWT_TOKEN_EXPIRATION = 600

FLICKR_API_KEY = os.environ.get('FLICKR_API_KEY', None)
FLICKR_API_SECRET = os.environ.get('FLICKR_API_SECRET', None)