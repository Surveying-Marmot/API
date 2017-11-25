import unittest2 as unittest
import json
from app import app, db
from app.models import User, BetaCode
import base64
import time

class Test_Integration_User_Authentication(unittest.TestCase):
    """ All the test cases around the user manipulation """
    ENTRYPOINT_AUTH = app.config['BASE_URL']+'/user/auth'

    AUTHORIZATION_JDOE = 'Basic am9obmRvZToxMjM0NTY='       # Correct
    AUTHORIZATION_WRONG_PASS = 'Basic am9obmRvZToxMjM0NTY3' # Incorrect password
    AUTHORIZATION_WRONG_USER = 'Basic am9obmRvZTE6MTIzNDU2' # Incorrect username

    def setUp(self):
        self.app = app.test_client()
        db.create_all()

        # Add some users
        user1 = User(
            username='johndoe',
            email='johndoe@foo.bar'
        )
        user1.hash_password("123456")

        db.session.add(user1)
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_authentication_random_token(self):
        """ Test for a random string as a token """
        response = self.app.get(
            self.ENTRYPOINT_AUTH,
            headers={'Authorization': 'Basic testme'},
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            401
        )
        self.assertEqual(
            response.data,
            'Unauthorized Access'
        )

    def test_user_authentication_valid(self):
        """ Test valid user authentication """
        response = self.app.post(
            self.ENTRYPOINT_AUTH,
            headers={'Authorization': self.AUTHORIZATION_JDOE},
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertTrue('token' in response.data)

    def test_user_authentication_invalid(self):
        """ Test invalid user authentication """
        response = self.app.post(
            self.ENTRYPOINT_AUTH,
            headers={'Authorization': self.AUTHORIZATION_WRONG_USER},
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            401
        )
        self.assertEqual(
            response.data,
            'Unauthorized Access'
        )
        response = self.app.post(
            self.ENTRYPOINT_AUTH,
            headers={'Authorization': self.AUTHORIZATION_WRONG_PASS},
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            401
        )
        self.assertEqual(
            response.data,
            'Unauthorized Access'
        )

    def test_user_authentication_valid_token(self):
        """ Test valid token validation """
        response = self.app.post(
            self.ENTRYPOINT_AUTH,
            headers={'Authorization': self.AUTHORIZATION_JDOE},
            follow_redirects=True
        )
        token_str = json.loads(response.data)['token'] + ":*"
        token = base64.b64encode(token_str.encode())

        response = self.app.get(
            self.ENTRYPOINT_AUTH,
            headers={'Authorization': 'Basic '+token},
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            200
        )

    def test_user_authentication_expired_token(self):
        """ Test expired token validation """
        response = self.app.post(
            self.ENTRYPOINT_AUTH,
            headers={'Authorization': self.AUTHORIZATION_JDOE},
            follow_redirects=True
        )
        token_str = json.loads(response.data)['token'] + ":*"
        token = base64.b64encode(token_str.encode())

        time.sleep(5)

        response = self.app.get(
            self.ENTRYPOINT_AUTH,
            headers={'Authorization': 'Basic '+token},
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            401
        )
        self.assertEqual(
            response.data,
            'Unauthorized Access'
        )