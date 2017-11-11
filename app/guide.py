from app import app, db, auth, api
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Guide, User
from flask import g

image_fields = {
    'origin': fields.String,
    'flickr_id': fields.String,
    'url': fields.String,
    'latitude': fields.String,
    'longitude': fields.String
}

guide_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'photos': fields.List(fields.Nested(image_fields)),
    'creation': fields.DateTime
}

class GuideListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No guide title provided',
                                   location='json')
        super(GuideListAPI, self).__init__()

    def get(self):
        """ Get all the guides of from the current user """
        guides = g.user.guides.all()

        return marshal(guides, guide_fields)

    def post(self):
        args = self.reqparse.parse_args()

        guide = Guide(title=args['title'], owner=g.user)
        db.session.add(guide)
        db.session.commit()
        return marshal(guide, guide_fields)


class GuideAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='No guide id provided')
        super(GuideAPI, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        guide = Guide.query.get(args['id'])

        return marshal(guide, guide_fields)

api.add_resource(GuideListAPI, app.config['BASE_URL']+'/guides', endpoint='guides')


api.add_resource(GuideAPI, app.config['BASE_URL']+'/guide', endpoint='guide')

# class GuideAPI(Resource):
#     @auth.login_required
#     def post(self):
