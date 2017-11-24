from app import app, db, auth, api
from flask import Flask, request, url_for, jsonify, abort, g
from flask_restful import Resource, reqparse, fields, marshal
from app.models import User, BetaCode, Lens, ExpiredToken, BadSignatureToken
import re

from app.fields.user import *

# User authentication
# https://photoscout.github.io/API-Documentation/#user-user-authentication

class UserAuthentication_API(Resource):
    """ API entrypoint dealing with user authentication """
    decorators = [auth.login_required]

    def get(self):
        """ Check that a JWT token is still valid """
        # The error case is dealt with by the login_required decorator
        return {},200

    def post(self):
        """ Create and return a JWT token if user authenticate """
        token = g.user.generate_auth_token()
        return {'token': token.decode('ascii')}, 200

api.add_resource(
    UserAuthentication_API,
    app.config['BASE_URL']+'/user/auth',
    endpoint='user_authentication'
)

# User administration
# https://photoscout.github.io/API-Documentation/#user-user-administration

class UserAdministration_API(Resource):
    """ API entrypoint dealing with user administration """
    def post(self):
        """ Create a new user """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument(
            'username',
            type=str,
            required=True,
            help='No username was provided'
        )
        parser.add_argument(
            'email',
            type=str,
            required=True,
            help='No email was provided'
        )
        parser.add_argument(
            'password',
            type=str,
            required=True,
            help='No password was provided'
        )
        parser.add_argument(
            'code',
            type=str,
            required=True,
            help='No beta code was provided'
        )
        args = parser.parse_args()

        # Check that the beta code is valid
        betacode = BetaCode.query.filter_by(code=args['code']).first()
        if not betacode:
            return {'error': 'Code is invalid'}, 400

        # Check that the username is not already in use
        if User.query.filter_by(username=args['username']).first():
            return {'error': 'Username already in use'}, 409

        # Create the new user
        user = User(username=args['username'], email=args['email'])
        user.hash_password(args['password'])
        db.session.add(user)

        # Delete the beta code
        db.session.delete(betacode)

        db.session.commit()

        return {},201

    @auth.login_required
    def delete(self):
        """ Delete a user """
        db.session.delete(g.user)
        db.session.commit()
        return {},200

api.add_resource(
    UserAdministration_API,
    app.config['BASE_URL']+'/user',
    endpoint='user_administration'
)

# User information
# https://photoscout.github.io/API-Documentation/#user-user-info

class UserInfo_API(Resource):
    """ API entrypoint dealing with user information """
    decorators = [auth.login_required]

    def get(self):
        """ Get all the available info about himself """
        return marshal(g.user, USER_FIELDS), 200

    def patch(self):
        """ Modify the given data in the current user """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument(
            'fullname',
            type=str,
            required=False,
            location='json'
        )
        parser.add_argument(
            'password',
            type=dict,
            required=False,
            location='json'
        )
        parser.add_argument(
            'email',
            type=str,
            required=False,
            location='json'
        )
        args = parser.parse_args()

        # Make the changes for the fullname
        if not args.fullname is None:
            g.user.fullname = args.fullname.strip()

        # Make the changes for the password
        if args.password:
            # Parse the password field
            pass_parser = reqparse.RequestParser()
            pass_parser.add_argument('new', type=str, location=('password',),
            required=True)
            pass_parser.add_argument('old', type=str, location=('password',), required=True)
            pass_args = pass_parser.parse_args(req=args)

            # First check the old password
            if not g.user.verify_password(pass_args.old):
                return {'error': 'Old password invalid'}, 400

            g.user.hash_password(pass_args.new)

        # Make the changes for the email
        if not args.email is None:
            # Check if empty
            if not args.email.strip():
                return {'error': 'Mandatory fields cannot be empty'}, 400
            # Check the format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", args.email):
                return {'error': 'Email format is invalid'}, 400

            g.user.email = args.email

        # Finally if all went fine, commit and return
        db.session.commit()

        return marshal(g.user, USER_FIELDS), 200

api.add_resource(
    UserInfo_API,
    app.config['BASE_URL']+'/user/info',
    endpoint='user_information'
)

# Other users information
# https://photoscout.github.io/API-Documentation/#user-other-users-info

class OtherUserInfo_API(Resource):
    """ API entrypoint dealing with other users information """

    def get(self, username):
        """ Return the short information about another user """
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'error': 'No user found'}, 404

        return marshal(user, USER_SHORT_FIELDS), 200

api.add_resource(
    OtherUserInfo_API,
    app.config['BASE_URL']+'/user/info/<string:username>',
    endpoint='otherusers_information'
)

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    try:
        user = User.verify_auth_token(username_or_token)
    except (ExpiredToken, BadSignatureToken):
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True
