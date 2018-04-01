from app import app, db, auth, api
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Guide, User, Photo
import datetime
from flask import g
import flickrapi
import re

from app.fields.guide import *
from app.fields.photo import *


FLICKR = flickrapi.FlickrAPI(
    app.config['FLICKR_API_KEY'],
    app.config['FLICKR_API_SECRET'],
    format='parsed-json'
)

# Public guides listing
# https://photoscout.github.io/API-Documentation/#guide-public-guides-listing

class GuidePublicListing_API(Resource):
    """ API entrypoint returning the list of publicly available guides """

    def get(self):
        """ Get the list """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        args = parser.parse_args()

        # Setting the defaults
        page = args.page if args.page else 0
        per_page = args.per_page if args.per_page else 10


        guides = Guide.query.filter_by(visibility=1).offset(per_page*page).limit(per_page).all()

        return marshal(guides, GUIDE_SHORT_FIELDS)

api.add_resource(
    GuidePublicListing_API,
    app.config['BASE_URL']+'/public/guides',
    endpoint='guide_public_listing'
)

# Guides listing
# https://photoscout.github.io/API-Documentation/#guide-guides-listing

class GuideListing_API(Resource):
    """ API entrypoint returning the list of user guides """
    decorators = [auth.login_required]

    def get(self):
        """ Get the list """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        args = parser.parse_args()

        # Setting the defaults
        page = args.page if args.page else 0
        per_page = args.per_page if args.per_page else 20

        guides = g.user.guides.offset(per_page*page).limit(per_page).all()

        return marshal(guides, GUIDE_FIELDS)

api.add_resource(
    GuideListing_API,
    app.config['BASE_URL']+'/guides',
    endpoint='guide_listing'
)

# Guide
# https://photoscout.github.io/API-Documentation/#guide-guide

class Guide_API(Resource):
    """ API entrypoint for manipulating a guide """
    decorators = [auth.login_required]

    def get(self):
        """ Get all the guide information """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument(
            'guide_id',
            # type=int,
            type=str,
            required=True,
            help='No guide id was provided'
        )
        args = parser.parse_args()

        # guide = Guide.query.get(args.guide_id)
        guide = Guide.query.filter_by(short_name=args.guide_id).first()

        if not guide:
            return {'error': 'Guide not found'}, 404

        return marshal(guide, GUIDE_FIELDS), 200

    def post(self):
        """ Create a new guide """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument(
            'title',
            type=str,
            required=True,
            help='No guide title was provided',
            location='json'
        )
        args = parser.parse_args()

        guide = Guide(title=args.title, short_name=args.title[:32].replace(' ', '-').lower(), owner=g.user)
        db.session.add(guide)
        db.session.commit()

        return marshal(guide, GUIDE_FIELDS), 200

    def patch(self):
        """ Edit the guide information """
        parser = reqparse.RequestParser()
        parser.add_argument(
            'guide_id',
            type=int,
            required=True,
            help='No guide id was provided',
            location='json'
        )
        parser.add_argument(
            'guide_info',
            type=dict,
            required=True,
            help='No guide info was provided',
            location='json'
        )
        args = parser.parse_args()

        info_parser = reqparse.RequestParser()
        info_parser.add_argument('title', type=str, location=('guide_info',))
        info_parser.add_argument('featured_photo', type=int, location=('guide_info',))
        info_parser.add_argument('visibility', type=bool, location=('guide_info',))
        info_parser.add_argument('location', type=dict, location=('guide_info',))
        info_args = info_parser.parse_args(req=args)

        guide = Guide.query.get(args.guide_id)

        print(info_args)

        if not guide:
            return {'error': 'Guide not found'}, 404

        # Make the change for the title
        if not info_args.title is None:
            # Check if empty
            if not info_args.title.strip():
                return {'error': 'Title cannot be empty'}, 400
            guide.title = info_args.title

        # Make the change for the featured photo
        if not info_args.featured_photo is None:
            photo = Photo.query.get(info_args.featured_photo)

            if not photo or not photo in guide.photos:
                return {'error': 'Featured image is not part of the guide'}, 400

            guide.featured_photo = photo.url

        # Make the change for the visibility
        if not info_args.visibility is None:
            guide.visibility = info_args.visibility

        db.session.commit()

        return marshal(guide, GUIDE_FIELDS), 200

    def delete(self):
        """ Delete a guide """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument(
            'guide_id',
            type=int,
            required=True,
            help='No guide id was provided',
            location='json'
        )
        args = parser.parse_args()

        guide = Guide.query.get(args.guide_id)

        if not guide:
            return {'error': 'Guide not found'}, 404

        db.session.delete(guide)
        db.session.commit()
        return {},200

api.add_resource(
    Guide_API,
    app.config['BASE_URL']+'/guide',
    endpoint='guide'
)

# Guide's photo interaction
# https://photoscout.github.io/API-Documentation/#guide-guide-s-photos-interaction

class Guide_Photo_API(Resource):
    """ API entrypoint for manipulating a guide's photo """
    decorators = [auth.login_required]

    def get(self):
        """ Get a list of all photos in a guide """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument('guide_id', type=str, required=True, help='No guide id was provided', location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        args = parser.parse_args()

        guide = Guide.query.filter_by(short_name=args.guide_id).first()

        if not guide:
            return {'error': 'Guide not found'}, 404

        # Setting the defaults
        page = args.page if args.page else 0
        per_page = args.per_page if args.per_page else 50

        photos = guide.photos.offset(per_page*page).limit(per_page).all()

        return marshal(photos, PHOTO_FIELDS)

    def delete(self):
        """ Remove a photo from a guide """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument('guide_id', type=str, required=True, help='No guide id was provided')
        parser.add_argument('photo_id', type=int, required=True, help='No photo id was provided')
        args = parser.parse_args()

        guide = Guide.query.filter_by(short_name=args.guide_id).first()

        if not guide:
            return {'error': 'Guide not found'}, 404

        photo = Photo.query.get(args.photo_id)

        if not photo in guide.photos:
            return {'error': 'Photo not in guide'}, 404

        guide.photos.remove(photo)

        # Let's not create orphans
        if photo.is_orphan():
            db.session.delete(photo)

        db.session.commit()
        return {},200

    def post(self):
        """ Add a photo to a guide """
        # Create the request parser
        parser = reqparse.RequestParser()
        parser.add_argument('guide_id', type=str, required=True, help='No guide id was provided', location='json')
        parser.add_argument('image', type=dict, required=True, help='No photo info was provided', location='json')
        args = parser.parse_args()

        info_parser = reqparse.RequestParser()
        info_parser.add_argument('origin', type=str, required=True, location=('image',))
        info_parser.add_argument('id', type=str, required=True, location=('image',))
        info_args = info_parser.parse_args(req=args)

        guide = Guide.query.filter_by(short_name=args.guide_id).first()

        if not guide:
            return {'error': 'Guide not found'}, 404

        photo = Photo.query.filter_by(
            flickr_id=info_args.id
        ).first()

        if photo == None:
            photo_data = FLICKR.photos.getInfo(
                photo_id=info_args.id
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
            flash_fired = 0
            exposure = ""
            try:
                photo_exif = FLICKR.photos.getExif(
                    photo_id=args['image']['id']
                )

                # Matching the lens model
                matching = [s for s in photo_exif['photo']['exif'] if "LensModel" in s['tag']]
                if matching != []:
                    matched = re.search( r'(\d{1,4}(?:\.0)?)(?:-(\d{1,4}(?:\.0)?))? ?mm', matching[0]['raw']['_content'], re.M|re.I)
                    if matched.group(2) == None:
                        lens_focal = matched.group(1)
                    else:
                        lens_focal = matched.group(1) + " " + matched.group(2)


                # Matching the flash
                matching = [s for s in photo_exif['photo']['exif'] if s['tag'] == "Flash"]
                if matching != []:
                    if "Fired" in matching[0]['raw']['_content']:
                        flash_fired = 1

                # Matching the exposure
                matching = [s for s in photo_exif['photo']['exif'] if s['tag'] == "ExposureTime"]
                if matching != []:
                    exposure = matching[0]['raw']['_content']
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
                lensFocal = lens_focal,
                flash_fired = flash_fired,
                exposure = exposure
            )
        else:
            if photo in guide.photos:
                return "already present"

        guide.photos.append(photo)
        db.session.commit()

        return marshal(photo, PHOTO_FIELDS)

api.add_resource(
    Guide_Photo_API,
    app.config['BASE_URL']+'/guide/photo',
    endpoint='guide_photo'
)