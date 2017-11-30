from app import app, db, auth, api
from flask import Flask, request, url_for, jsonify, abort, g
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Photo, Guide
import requests
from app.fields.places import *

class Google_Location():
    def __init__(self, place):
        self.latitude = place['geometry']['location']['lat']
        self.longitude = place['geometry']['location']['lng']

        self.name = place['name']
        if 'photos' in place:
            self.image = self.getImage(place['photos'][0]['photo_reference'])

    def getImage(self, ref):
        url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + ref + "&key="+app.config['GOOGLE_KEY']

        response = requests.get(url)
        return response.url


class Location_API(Resource):
    decorators = [auth.login_required]

    def get(self):
        """ Get the location nearby the guide """
        parser = reqparse.RequestParser()

        # Get the guide ID
        parser.add_argument(
            'id',
            type=int,
            required=True,
            help="Missing guide id"
        )

        args = parser.parse_args()

        guide = Guide.query.get(args.id)

        # Get the guide location
        location = Guide.getFeaturedLocation(guide)
        print(location)

        if location:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + location['latitude']+"," + location['longitude'] + "&radius=1000&keyword=point of interest&key="+app.config['GOOGLE_KEY']

            response = requests.get(url)

            place_list = []

            for res in response.json()['results']:
                res_full = Google_Location(res)
                place_list.append(res_full)

            return marshal(place_list, PLACE_FIELDS), 200

        # No location available for this guide
        else:
            return "No location", 404

api.add_resource(
    Location_API,
    app.config['BASE_URL']+'/guide/near',
    endpoint='location'
)

# https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522,151.1957362&radius=500&type=restaurant&keyword=cruise&key=YOUR_API_KEY