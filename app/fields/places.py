"""
    Place response fields definition used for marshaling
"""

from flask_restful import fields

PLACE_FIELDS = {
    'name': fields.String,
    'latitude': fields.String,
    'longitude': fields.String,
    'image': fields.String
}