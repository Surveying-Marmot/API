"""
    Misc response fields definition used for marshaling
"""

from flask_restful import fields

LOCATION_FIELDS = {
    'latitude': fields.String,
    'longitude': fields.String
}