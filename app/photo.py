from app import app, db, auth, api
from flask import Flask, request, url_for, jsonify, abort, g
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Photo, Guide
import datetime
import flickrapi

FLICKR = flickrapi.FlickrAPI(
    app.config['FLICKR_API_KEY'],
    app.config['FLICKR_API_SECRET'],
    format='parsed-json'
)

class PhotoSearch_API(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(PhotoSearch_API, self).__init__()

    def get(self):
        """ Get a list of photos from the target api """
        parser = reqparse.RequestParser()

        # List of keywords
        parser.add_argument(
            'keywords',
            type=str,
            required=True,
            help="Missing list of keywords"
        )
        # Page to load from the target api
        parser.add_argument(
            'page',
            type=int,
            required=False,
            help="Error in target page"
        )

        args = parser.parse_args()

        try:
            images = FLICKR.photos.search(
                text=args['keywords'],
                per_page='50',
                sort="relevance",
                content_type=1,
                # Also include GPS, date, and author info
                extras="geo,date_taken,owner_name"
            )

            return jsonify(images)

        except flickrapi.FlickrError:
            abort(400)

class PhotoSelect_API(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(PhotoSelect_API, self).__init__()

    @staticmethod
    def image_data_parser(image):
        if image['origin'] != "flickr":
            raise ValueError("Origin must be Flickr")
        if image['id'] == None:
            raise ValueError("ID must be specified")

        return image

    def put(self):
        """ Add an image to a guide """
        parser = reqparse.RequestParser()

        # Guide to which add the photo
        parser.add_argument(
            'guide',
            type=int,
            required=True,
            help="Missing guide ID"
        )
        # Image to add
        parser.add_argument(
            'image',
            type=self.image_data_parser,
            required=True
        )

        args = parser.parse_args()

        guide = Guide.query.get(args['guide'])
        guide.last_edited = datetime.datetime.now()

        photo = Photo.query.filter_by(
            flickr_id=args['image']['id']
        ).first()

        if photo == None:
            photo_data = FLICKR.photos.getInfo(
                photo_id=args['image']['id']
            )
            print('herex')
            print(photo_data)

            latitude = ""
            longitude = ""

            # Check that the image is tagged with geoloc
            if 'location' in photo_data['photo']:
                latitude = photo_data['photo']['location']['latitude']
                longitude = photo_data['photo']['location']['longitude']

            photo = Photo(
                origin='Flickr',
                flickr_id=args['image']['id'],
                url='https://farm'+ str(photo_data['photo']['farm']) +'.staticflickr.com/'+  str(photo_data['photo']['server']) +'/'+ str(photo_data['photo']['id']) +'_'+ str(photo_data['photo']['secret']) +'.jpg',
                latitude = latitude,
                longitude = longitude
            )
        else:
            if photo in guide.photos:
                return "already present"

        guide.photos.append(photo)
        db.session.commit()

        return "success"

    def delete(self):
        """ Remove an image from a guide """
        parser = reqparse.RequestParser()

        # Guide to which add the photo
        parser.add_argument(
            'guide',
            type=int,
            required=True,
            help="Missing guide ID"
        )
        # Image to add
        parser.add_argument(
            'image',
            type=self.image_data_parser,
            required=True
        )

        args = parser.parse_args()

        photo = Photo.query.filter_by(
            flickr_id=args['image']['id']
        ).first()

        if not photo == None:
            guide = Guide.query.get(args['guide'])
            guide.last_edited = datetime.datetime.now()
            guide.photos.remove(photo)
            db.session.commit()
            return "success"

        return "error"


api.add_resource(
    PhotoSearch_API,
    app.config['BASE_URL']+'/photos/search',
    endpoint='photos_search'
)

api.add_resource(
    PhotoSelect_API,
    app.config['BASE_URL']+'/photos/selected',
    endpoint='photos_selected'
)
