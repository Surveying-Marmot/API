from app import app, db, auth, api
from flask import Flask, request, url_for, jsonify, abort, g
from flask_restful import Resource, reqparse, fields, marshal
from app.models import User, BetaCode, Lens, ExpiredToken, BadSignatureToken
import re

lens_fields = {
    'display_name': fields.String,
    'focal_range': fields.String
}

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
    UserGear_API,
    app.config['BASE_URL']+'/user/gear',
    endpoint='user_gear'
)
