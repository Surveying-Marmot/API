"""
    Image response fields definition used for marshaling
"""

from flask_restful import fields
from .misc import LOCATION_FIELDS

PHOTO_FIELDS = {
    'id': fields.Integer,
    'origin': fields.String,
    'title': fields.String,
    'flickr_id': fields.String,
    'author': fields.String,
    'url': fields.String,
    'location': fields.Nested(LOCATION_FIELDS),
    'lensFocal': fields.String
}