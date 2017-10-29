from app import app, db, auth, api
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Guides, Users
from flask import g

guide_fields = {
    'title': fields.String
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

        guide = Guides(title=args['title'], owner=g.user)
        db.session.add(guide)
        db.session.commit()


api.add_resource(GuideListAPI, app.config['BASE_URL']+'/guides', endpoint='guides')

# class GuideAPI(Resource):
#     @auth.login_required
#     def post(self):
