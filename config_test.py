"""
    Defines a set a config variables for testing the application
"""

import os

DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DIR, 'test.db')

TESTING = True
WTF_CSRF_ENABLED = False

BASE_URL = '/api/v1'

API_SECRET_KEY = 'testtesttesttesttesttesttesttest'

JWT_TOKEN_EXPIRATION = 3

FLICKR_API_KEY = ""
FLICKR_API_SECRET = ""