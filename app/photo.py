from app import app, db, auth, api
from flask import Flask, request, url_for, jsonify, abort, g
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Photo, Guide
import datetime
import flickrapi
import re

FLICKR = flickrapi.FlickrAPI(
    app.config['FLICKR_API_KEY'],
    app.config['FLICKR_API_SECRET'],
    format='parsed-json'
)

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
            type=unicode,
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
        page = 1
        if args['page']:
            page = args['page']

        try:
            images = FLICKR.photos.search(
                text=args['keywords'],
                per_page='20',
                sort="relevance",
                content_type=1,
                page=page,
                # Also include GPS, date, and author info
                extras="geo,date_taken,owner_name"
            )

            return jsonify(images)

        except flickrapi.FlickrError:
            abort(400)

class PhotoSearchNear_API(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        super(PhotoSearchNear_API, self).__init__()

    def get(self):
        """ Get a list of photos from the target api near a location """
        parser = reqparse.RequestParser()

        print("here")

        # List of keywords
        parser.add_argument(
            'lat',
            type=str,
            required=True,
            help="Missing lat"
        )

        parser.add_argument(
            'lon',
            type=str,
            required=True,
            help="Missing lat"
        )
        # Page to load from the target api
        parser.add_argument(
            'page',
            type=int,
            required=False,
            help="Error in target page"
        )

        args = parser.parse_args()
        page = 1
        if args['page']:
            page = args['page']

        print("Here")
        print(args['lat'])
        print(args['lon'])

        try:
            images = FLICKR.photos.search(
                lat=args['lat'],
                lon=args['lon'],
                per_page='25',
                # radius='2',
                sort="interestingness-desc",
                content_type=1,
                page=page,
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

            # Get the photographer name
            username = photo_data['photo']['owner']['username']
            realname = photo_data['photo']['owner']['realname']

            author = username if realname == "" else realname

            # Check that the image is tagged with geoloc
            latitude = ""
            longitude = ""
            if 'location' in photo_data['photo']:
                latitude = photo_data['photo']['location']['latitude']
                longitude = photo_data['photo']['location']['longitude']

            # Try to get the exif
            lens_focal = ""
            try:
                photo_exif = FLICKR.photos.getExif(
                    photo_id=args['image']['id']
                )

                matching = [s for s in photo_exif['photo']['exif'] if "LensModel" in s['tag']]
                if matching != []:
                    print(matching[0]['raw']['_content'])
                    matched = re.search( r'(\d{1,4}(?:\.0)?)(?:-(\d{1,4}(?:\.0)?))? ?mm', matching[0]['raw']['_content'], re.M|re.I)
                    if matched.group(2) == None:
                        lens_focal = matched.group(1)
                    else:
                        lens_focal = matched.group(1) + " " + matched.group(2)
            except flickrapi.FlickrError:
                pass

            photo = Photo(
                origin='Flickr',

                title=photo_data['photo']['title']['_content'],
                author=author,

                flickr_id=args['image']['id'],
                url='https://farm'+ str(photo_data['photo']['farm']) +'.staticflickr.com/'+  str(photo_data['photo']['server']) +'/'+ str(photo_data['photo']['id']) +'_'+ str(photo_data['photo']['secret']) +'.jpg',
                latitude = latitude,
                longitude = longitude,
                lensFocal = lens_focal
            )
        else:
            if photo in guide.photos:
                return "already present"

        guide.photos.append(photo)
        db.session.commit()

        return marshal(photo, image_fields)

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
    PhotoSearchNear_API,
    app.config['BASE_URL']+'/photo/search/near',
    endpoint='photos_search_near'
)

api.add_resource(
    PhotoSearch_API,
    app.config['BASE_URL']+'/photo/search',
    endpoint='photos_search'
)

api.add_resource(
    PhotoSelect_API,
    app.config['BASE_URL']+'/photos/selected',
    endpoint='photos_selected'
)
