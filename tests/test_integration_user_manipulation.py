import unittest2 as unittest
import json
from app import app, db
from app.models import User, BetaCode
import base64
import time

class Test_Integration_User_Manipulation(unittest.TestCase):
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

    def test_user_manipulation_delete_user_token(self):
        """ Test deleting user without token """
        response = self.app.delete(
            self.ENTRYPOINT_USER,
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, 'Unauthorized Access')

    def test_user_manipulation_delete_user(self):
        """ Test deleting user with token """
        response = self.app.delete(
            self.ENTRYPOINT_USER,
            headers=self.login_get_token_header('johndoe1', '123456') ,
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.get_user('johndoe1'))

    def test_user_manipulation_edit_fullname_token(self):
        """ Test editing user without token """
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps({'fullname': 'John Doe'})
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, 'Unauthorized Access')

    def test_user_manipulation_edit_fullname(self):
        """ Test editing user fullname """
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456') ,
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps({'fullname': 'John Doe'})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_user('johndoe').fullname, 'John Doe')

    def test_user_manipulation_edit_empty_fullname(self):
        """ Test emptying user fullname """
        self.get_user('johndoe').fullname = 'John Doe'
        db.session.commit()

        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps({'fullname': ''})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_user('johndoe').fullname, '')

    def test_user_manipulation_edit_email(self):
        """ Test editing user email """
        self.get_user('johndoe').email = ''
        db.session.commit()
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps({'email': 'john.doe@foo.bar'})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_user('johndoe').email, 'john.doe@foo.bar')

    def test_user_manipulation_edit_invalid_email(self):
        """ Test invalid user email edition """
        prev_email = self.get_user('johndoe').email
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps({'email': ''})
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {'error': 'Mandatory fields cannot be empty'})
        self.assertEqual(self.get_user('johndoe').email, prev_email)

        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps({'email': 'test me'})
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {'error': 'Email format is invalid'})
        self.assertEqual(self.get_user('johndoe').email, prev_email)

    def test_user_manipulation_edit_password_mising(self):
        """ Test editing user password with missing fields """

        # Testing not object pass
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps({'password': 'pass'})
        )
        self.assertEqual(response.status_code, 400)

        # Testing missing new
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps(
                {
                    'password': {
                        'old': 'pass'
                    }
                }
            )
        )
        self.assertEqual(response.status_code, 400)

        # Testing missing new
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps(
                {
                    'password': {
                        'new': 'pass'
                    }
                }
            )
        )
        self.assertEqual(response.status_code, 400)

    def test_user_manipulation_edit_password_invalid_old(self):
        """ Test editing user password with invalid old password"""
        prev_pass = self.get_user('johndoe').password
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps(
                {
                    'password': {
                        'old': '456789',
                        'new': '456789'
                    }
                })
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(prev_pass, self.get_user('johndoe').password)

    def test_user_manipulation_edit_password(self):
        """ Test editing user password """
        prev_pass = self.get_user('johndoe').password
        response = self.app.patch(
            self.ENTRYPOINT_INFO,
            headers=self.login_get_token_header('johndoe', '123456'),
            follow_redirects=True,
            content_type='application/json',
            data=json.dumps(
                {
                    'password': {
                        'old': '123456',
                        'new': '456789'
                    }
                })
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(prev_pass, self.get_user('johndoe').password)

        # Try to login
        response = self.app.post(
            self.ENTRYPOINT_AUTH,
            headers=self.create_authorization_header('johndoe', '456789'),
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            200
        )

        # Put everything back
        self.get_user('johndoe').password = prev_pass
        db.session.commit()