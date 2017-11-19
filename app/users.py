from app import app, db, auth, api
from flask import Flask, request, url_for, jsonify, abort, g
from flask_restful import Resource, reqparse, fields, marshal
from app.models import User, Lens
import re

@app.route(app.config['BASE_URL']+"/users/create", methods=["POST"])
def create_user():
    """ Create a new user """

    # Validate the inputs
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        abort(400)
    if User.query.filter_by(username = username).first() is not None:
        abort(400)

    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({ 'username': user.username }), 201

@app.route(app.config['BASE_URL']+'/users/login')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@app.route(app.config['BASE_URL']+'/users/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'fullname': fields.String
}

lens_fields = {
    'display_name': fields.String,
    'focal_range': fields.String
}

# API for the user
class UserInfo_API(Resource):
    """ API entrypoint to get info about a user """
    decorators = [auth.login_required]

    def get(self):
        """ Get all the available info about himself """
        return marshal(g.user, user_fields)

    def put(self):
        """ Modify the given data in the current user """

        parser = reqparse.RequestParser()
        parser.add_argument('label', type=str, required=True,
                                   help='No field label provided',
                                   location='json')
        parser.add_argument('data', type=str, required=True,
                                   help='No new data provided',
                                   location='json')

        parser.add_argument('oldpass', type=str,
                                   location='json')

        args = parser.parse_args()

        if args.label == "fullname":
            g.user.fullname = args.data

        if args.label == "password":
            if g.user.verify_password(args.oldpass):
                g.user.hash_password(args.data)

        db.session.commit()

        return "success"

# API for user gear
class UserGear_API(Resource):
    """ API entrypoint to get list of the user gear """
    decorators = [auth.login_required]

    def get(self):
        """ Get all the lenses of the current user """
        lenses = g.user.lenses.all()

        return marshal(lenses, lens_fields)

    def post(self):
        """ Add a new lens to the current user """
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                                   help='No name was provided',
                                   location='json')

        args = parser.parse_args()

        lens_focal = ""

        matched = re.search( r'(\d{1,4}(?:\.0)?)(?:-(\d{1,4}(?:\.0)?))? ?mm', args['name'], re.M|re.I)
        if matched.group(2) == None:
            lens_focal = matched.group(1)
        else:
            lens_focal = matched.group(1) + " " + matched.group(2)

        if lens_focal == "":
            return {"error", 400}

        lens = Lens(
            display_name=args['name'],
            focal_range=lens_focal,
            owner=g.user
        )
        db.session.add(lens)
        db.session.commit()

        return marshal(lens, lens_fields)

api.add_resource(
    UserInfo_API,
    app.config['BASE_URL']+'/user',
    endpoint='user_info'
)

api.add_resource(
    UserGear_API,
    app.config['BASE_URL']+'/user/gear',
    endpoint='user_gear'
)