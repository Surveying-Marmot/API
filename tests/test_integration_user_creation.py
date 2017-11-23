import unittest2 as unittest
import json
from app import app, db
from app.models import User, BetaCode

class Test_Integration_User_Creation(unittest.TestCase):
    """ All the test cases around the user creation """
    ENTRYPOINT = app.config['BASE_URL']+'/user'

    def setUp(self):
        self.app = app.test_client()
        db.create_all()

        # Add some beta codes
        code1 = BetaCode(code='9Kv34ZC36WCZisFy') # Valid user
        code2 = BetaCode(code='Z789cTsY8Gnntbmp') # Username double 1
        code3 = BetaCode(code='MviAKaFnrgtru86S') # Username double 2
        code4 = BetaCode(code='NHBStytEPmppU6Rx') # Code deletion
        db.session.add(code1)
        db.session.add(code2)
        db.session.add(code3)
        db.session.add(code4)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_creation_no_data(self):
        """ Test user creation without data """
        response = self.app.post(
            self.ENTRYPOINT,
            content_type='application/json',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

    def test_user_creation_wrong_code(self):
        """ Test user creation with wrong beta code """
        data = {
            'username': 'test_user_creation_wrong_code',
            'email': 'johndoe@foo.bar',
            'password': '123456',
            'code': 'abcdef'
        }
        response = self.app.post(
            self.ENTRYPOINT,
            content_type='application/json',
            data=json.dumps(data),
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            400
        )
        self.assertEqual(
            json.loads(response.data),
            {'error': 'Code is invalid'}
        )

    def test_user_creation_valid(self):
        """ Test valid user creation """
        data = {
            'username': 'test_user_creation_valid',
            'email': 'johndoe@foo.bar',
            'password': '123456',
            'code': '9Kv34ZC36WCZisFy'
        }
        response = self.app.post(
            self.ENTRYPOINT,
            content_type='application/json',
            data=json.dumps(data),
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            201
        )

        # Double check that it is in DB
        user = User.query.filter_by(username='test_user_creation_valid').first()
        self.assertTrue(user)

    def test_user_creation_reused_username(self):
        """ Test multiple use of the same username """
        data = {
            'username': 'test_user_creation_reused_username',
            'email': 'johndoe@foo.bar',
            'password': '123456',
            'code': 'Z789cTsY8Gnntbmp'
        }
        response = self.app.post(
            self.ENTRYPOINT,
            content_type='application/json',
            data=json.dumps(data),
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            201
        )
        data = {
            'username': 'test_user_creation_reused_username',
            'email': 'johndoe@foo.bar',
            'password': '123456',
            'code': 'MviAKaFnrgtru86S'
        }
        response = self.app.post(
            self.ENTRYPOINT,
            content_type='application/json',
            data=json.dumps(data),
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            409
        )
        self.assertEqual(
            json.loads(response.data),
            {'error': 'Username already in use'}
        )

    def test_user_creation_reused_code(self):
        """ Test trying to use the same code twice """
        data = {
            'username': 'test_user_creation_reused_code',
            'email': 'johndoe@foo.bar',
            'password': '123456',
            'code': 'NHBStytEPmppU6Rx'
        }
        response = self.app.post(
            self.ENTRYPOINT,
            content_type='application/json',
            data=json.dumps(data),
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            201
        )
        data = {
            'username': 'test_user_creation_reused_code2',
            'email': 'johndoe@foo.bar',
            'password': '123456',
            'code': 'NHBStytEPmppU6Rx'
        }
        response = self.app.post(
            self.ENTRYPOINT,
            content_type='application/json',
            data=json.dumps(data),
            follow_redirects=True
        )
        self.assertEqual(
            response.status_code,
            400
        )
        self.assertEqual(
            json.loads(response.data),
            {'error': 'Code is invalid'}
        )