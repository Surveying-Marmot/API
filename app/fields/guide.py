"""
    Guide response fields definition used for marshaling
"""

from flask_restful import fields
from .misc import LOCATION_FIELDS

GUIDE_SHORT_FIELDS = {
    'id': fields.Integer,
    'title': fields.String,
    'featured_image': fields.String,
    'owner': fields.String
}

GUIDE_FIELDS = {
    'id': fields.Integer,
    'title': fields.String,
    'featured_image': fields.String,
    'creation': fields.DateTime,
    'last_edited': fields.DateTime,
    'visibility': fields.Boolean,
    'number_photo': fields.Integer,
    'location': fields.Nested(LOCATION_FIELDS)
}
