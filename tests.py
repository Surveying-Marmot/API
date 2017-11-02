import os
import unittest
import json
from app import app, db
from app.models import *

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING']=True
        app.config['WTF_CSRF_ENABLED']=False
        DIR = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DIR, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_creation(self):
        entrypoint='/api/v1/users/create'

        """ Test missing data """
        response = self.app.post(
            entrypoint,
            content_type='application/json',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

        """ Test correct insertion """
        data = {
            'username': 'test',
            'password': 'test'
        }

        response = self.app.post(
            entrypoint,
            content_type='application/json',
            data=json.dumps(data),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 201)

        expected = {'username':'test'}
        self.assertEqual(json.loads(response.data), expected)


        """ Test doubling username """
        response = self.app.post(
            entrypoint,
            content_type='application/json',
            data=json.dumps(data),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()