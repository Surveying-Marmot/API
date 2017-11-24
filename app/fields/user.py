"""
    User response fields definition used for marshaling
"""

from flask_restful import fields

USER_SHORT_FIELDS = {
    'id': fields.Integer,
    'username': fields.String,
    'fullname': fields.String
}

USER_FIELDS = {
    'id': fields.Integer,
    'username': fields.String,
    'fullname': fields.String,
    'email': fields.String
}
