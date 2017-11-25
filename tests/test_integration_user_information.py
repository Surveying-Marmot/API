import unittest2 as unittest
import json
from app import app, db
from app.models import User, BetaCode
import base64
import time

class Test_Integration_User_Information(unittest.TestCase):
    """ All the test cases around the user manipulation """
    ENTRYPOINT_USER = app.config['BASE_URL']+'/user'
    ENTRYPOINT_AUTH = app.config['BASE_URL']+'/user/auth'
    ENTRYPOINT_INFO = app.config['BASE_URL']+'/user/info'

    def setUp(self):
        self.app = app.test_client()
        db.create_all()

        # Add some users
        user1 = User(
            username='johndoe',
            email='johndoe@foo.bar'
        )
        user1.hash_password("123456")

        user2 = User(
            username='johndoe1',
            email='johndoe@foo.bar'
        )
        user2.hash_password("123456")

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_authorization_header(self, username, password):
        """ Create the authorization header """
        auth_str = username + ':' + password
        return {'Authorization': 'Basic ' + base64.b64encode(auth_str.encode())}

    def login_get_token_header(self, username, password):
        """ Login the user and return the token """
        response = self.app.post(
            self.ENTRYPOINT_AUTH,
            headers=self.create_authorization_header(username, password) ,
            follow_redirects=True
        )
        token_str = json.loads(response.data)['token']
        return self.create_authorization_header(token_str, '*')

    def get_user(self, username):
        return User.query.filter_by(username=username).first()

    def test_user_information_self_token(self):
        """ Test getting user info without token """
        response = self.app.get(
            self.ENTRYPOINT_INFO,
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, 'Unauthorized Access')

    def test_user_information_self(self):
        """ Test get information about himself """
        user = self.get_user('johndoe')
        data = {
            'id': user.id,
            'username': user.username,
            'fullname': user.fullname,
            'email': user.email
        }

        response = self.app.get(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), data)

    def test_user_information_other(self):
        """ Test get information about another user """
        user = self.get_user('johndoe1')
        data_email = {
            'id': user.id,
            'username': user.username,
            'fullname': user.fullname,
            'email': user.email
        }
        data = {
            'id': user.id,
            'username': user.username,
            'fullname': user.fullname
        }

        response = self.app.get(
            self.ENTRYPOINT_INFO+"/johndoe1",
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), data)
        self.assertNotEqual(json.loads(response.data), data_email)

    def test_user_information_other_invalid(self):
        """ Test get information about another user that doesn't exist """
        response = self.app.get(
            self.ENTRYPOINT_INFO+"/johndoe2",
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data), {"error": "No user found"})