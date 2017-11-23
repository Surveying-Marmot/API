"""
    This module deals with the definition of all the database models needed for the application
"""

from app import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous  import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


class Lens(db.Model):
    """ Represent a lens """
    __tablename__ = 'lenses'

    id = db.Column(db.Integer, primary_key=True)

    display_name = db.Column(db.String(256))
    focal_range = db.Column(db.String(64))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return 'Lens: %r' % (self.displayName)

class BetaCode(db.Model):
    """ Table containing the beta codes """
    __tablename__ = 'betacodes'
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(16))


class User(db.Model):
    """ Represents a user of the service """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))
    fullname = db.Column(db.String(256))

    email = db.Column(db.String(256))

    guides = db.relationship('Guide', backref='owner', lazy='dynamic')
    lenses = db.relationship('Lens', backref='owner', lazy='dynamic')

    def __repr__(self):
        return 'User: %r' % (self.username)

    def hash_password(self, password):
        """ Encrypts the given password before saving it in the entry """
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        """ Validate the given password against the DB one """
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self):
        """ Generate a JWT token for this account """
        token = Serializer(
            app.config['API_SECRET_KEY'],
            expires_in=app.config['JWT_TOKEN_EXPIRATION']
        )
        return token.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """ Check that the token received is still valid """
        gen_token = Serializer(app.config['API_SECRET_KEY'])
        try:
            data = gen_token.loads(token)
        except SignatureExpired:
            raise ExpiredToken() # valid token, but expired
        except BadSignature:
            raise BadSignatureToken() # invalid token
        user = User.query.get(data['id'])
        return user

class ExpiredToken(Exception):
    """ Exception raised when jwt token is expired """
    pass

class BadSignatureToken(Exception):
    """ Exception raised when jwt token is invalid """
    pass


""" Link for many-to-many relationship between photos and guides """
photo_guide = db.Table(
    'photo_guide',
    db.Column('guide_id', db.Integer, db.ForeignKey('guides.id')),
    db.Column('photo_id', db.Integer, db.ForeignKey('photos.id'))
)


class Guide(db.Model):
    """ Represents a travel guide """
    __tablename__ = 'guides'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(256))

    creation = db.Column(db.DateTime, default=db.func.now())
    last_edited = db.Column(db.DateTime, default=db.func.now())

    visibility = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photos = db.relationship('Photo', backref='guides', lazy='dynamic', secondary=photo_guide)

    def __repr__(self):
        return 'Guide: %r' % (self.title)


class Photo(db.Model):
    """
        Represent a photo stored in an external service (flickr/500px)
        Photo are linked in a many to many relationship to the guides
    """
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)

    origin = db.Column(db.Enum('Flickr', '500px', name='service_origin'))

    title = db.Column(db.Text())
    author = db.Column(db.String(256))

    flickr_id = db.Column(db.String(16))

    url = db.Column(db.Text())

    latitude = db.Column(db.String(16))
    longitude = db.Column(db.String(16))

    lensFocal = db.Column(db.String(16))

    def __repr__(self):
        return 'Photo: %r' % (self.id)
