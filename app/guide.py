from app import app, db, auth, api
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Guide, User
from flask import g

image_fields = {
    'origin': fields.String,
    'flickr_id': fields.String,
    'flickr_secret': fields.String
}

guide_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'photos': fields.List(fields.Nested(image_fields))
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

        print(guides[0].photos)

        return marshal(guides, guide_fields)

    def post(self):
        args = self.reqparse.parse_args()

        guide = Guide(title=args['title'], owner=g.user)
        db.session.add(guide)
        db.session.commit()


api.add_resource(GuideListAPI, app.config['BASE_URL']+'/guides', endpoint='guides')

# class GuideAPI(Resource):
#     @auth.login_required
#     def post(self):
