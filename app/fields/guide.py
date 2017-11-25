"""
    Guide response fields definition used for marshaling
"""

from flask_restful import fields
from .misc import LOCATION_FIELDS
from app.models import Guide

DEFAULT_FEATURED_PHOTO = 'https://avatars0.githubusercontent.com/u/33183345?s=200&v=4'

GUIDE_SHORT_FIELDS = {
    'id': fields.Integer,
    'title': fields.String,
    'featured_image': fields.String(attribute=Guide.getFeaturedImage, default=DEFAULT_FEATURED_PHOTO),
    'owner': fields.String(attribute='owner.username')
}

GUIDE_FIELDS = {
    'id': fields.Integer,
    'title': fields.String,
    'featured_image': fields.String(attribute=Guide.getFeaturedImage, default=DEFAULT_FEATURED_PHOTO),
    'creation': fields.DateTime,
    'last_edited': fields.DateTime,
    'visibility': fields.Boolean,
    'number_photo': fields.Integer(attribute=Guide.getNumberPhoto),
    'location': fields.Nested(LOCATION_FIELDS, attribute=Guide.getFeaturedLocation),
    'owner': fields.String(attribute='owner.username')
}
