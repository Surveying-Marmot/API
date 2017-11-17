from app import app, db, auth, api
from flask import Flask, request, url_for, jsonify, abort, g
from flask_restful import Resource, reqparse, fields, marshal
from app.models import Photo, Guide
import requests

class Weather_API(Resource):
    decorators = [auth.login_required]

    def get(self):
        """ Get the weather info at the guide location """
        parser = reqparse.RequestParser()

        # Get the guide ID
        parser.add_argument(
            'id',
            type=int,
            required=True,
            help="Missing guide id"
        )

        args = parser.parse_args()

        guide = Guide.query.get(args['id'])

        # Get the guide location
        latitude = ""
        longitude = ""

        for photo in guide.photos:
            if photo.latitude != "":
                latitude = photo.latitude
                longitude = photo.longitude
                break

        # No location available for this guide
        if latitude == "":
            return "No location"

        # Build url
        url = "http://api.openweathermap.org/data/2.5/forecast?lat=" + latitude+"&lon=" + longitude + "&APPID=" + app.config['OPENWEATHERMAP_KEY'] + "&units=metric"

        response = requests.get(url)
        return response.json()

api.add_resource(
    Weather_API,
    app.config['BASE_URL']+'/weather',
    endpoint='weather'
)