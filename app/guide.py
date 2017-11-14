from app import app, db, auth, api
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Guide, User
import datetime
from flask import g

image_fields = {
    'origin': fields.String,
    'title': fields.String,
    'author': fields.String,
    'flickr_id': fields.String,
    'url': fields.String,
    'latitude': fields.String,
    'longitude': fields.String,
    'lensFocal': fields.String
}

guide_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'photos': fields.List(fields.Nested(image_fields)),
    'creation': fields.DateTime,
    'last_edited': fields.DateTime,
    'visibility': fields.Boolean
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

class GuidePublicListAPI(Resource):
    def get(self):
        """ Get all the guides with public visibility """
        guides = Guide.query.filter_by(visibility=1).all()
        print(guides)

        return marshal(guides, guide_fields)

# Not so nice way of doing a login only inside check
@auth.login_required
def Gate() :
    return True

class GuideAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='No guide id provided')
        super(GuideAPI, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        guide = Guide.query.get(args['id'])

        print(guide.visibility)

        if guide.visibility == 1:
            return marshal(guide, guide_fields)
        else:
            if Gate() == True:
                return marshal(guide, guide_fields)
            else:
                return auth.auth_error_callback()

    @auth.login_required
    def delete(self):
        args = self.reqparse.parse_args()
        guide = Guide.query.get(args['id'])

        db.session.delete(guide)
        db.session.commit()

    @auth.login_required
    def put(self):
        """ Modify the given data in the guide """

        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True,
                                   help='No guide id provided')
        parser.add_argument('label', type=str, required=True,
                                   help='No field label provided',
                                   location='json')
        parser.add_argument('data', type=str, required=True,
                                   help='No new data provided',
                                   location='json')

        args = parser.parse_args()
        guide = Guide.query.get(args['id'])

        guide.last_edited = datetime.datetime.now()

        if args['label'] == "visibility":
            guide.visibility = args['data']

        db.session.commit()

        return "success"

api.add_resource(GuideListAPI, app.config['BASE_URL']+'/guides', endpoint='guides')

api.add_resource(GuidePublicListAPI, app.config['BASE_URL']+'/guides/public', endpoint='guidesPublic')

api.add_resource(GuideAPI, app.config['BASE_URL']+'/guide', endpoint='guide')

# class GuideAPI(Resource):
#     @auth.login_required
#     def post(self):
