""" Database toolkit for photo scout

Usage:
  data_toolkit.py flash
  data_toolkit.py exposure
  data_toolkit.py (-h | --help)
  data_toolkit.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

import os.path
import imp
from docopt import docopt
from migrate.versioning import api
from app.models import Photo
import app
from app import db
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
import random, string
import flickrapi
from config import *

FLICKR = flickrapi.FlickrAPI(FLICKR_API_KEY,FLICKR_API_SECRET,
    format='parsed-json'
)

def add_flash():
    """ Add flash information to existing photos """
    photos = Photo.query.all()

    for photo in photos:
        # photo = photos[i]
        try:
            photo_exif = FLICKR.photos.getExif(
                photo_id=photo.flickr_id
            )

            matching = [s for s in photo_exif['photo']['exif'] if s['tag'] == "Flash"]
            if matching != []:
                if "Fired" in matching[0]['raw']['_content']:
                    photo.flash_fired = 1
                else:
                    photo.flash_fired = 0
            else:
                photo.flash_fired = 0
        except flickrapi.FlickrError:
            pass
    db.session.commit()

def add_speed():
    """ Add speed information to existing photos """
    photos = Photo.query.all()

    for photo in photos:
    # for i in range(0,5):
        # photo = photos[i]
        try:
            photo_exif = FLICKR.photos.getExif(
                photo_id=photo.flickr_id
            )

            matching = [s for s in photo_exif['photo']['exif'] if s['tag'] == "ExposureTime"]
            if matching != []:
                photo.exposure = matching[0]['raw']['_content']
            else:
                photo.exposure = ""
        except flickrapi.FlickrError:
            pass

    db.session.commit()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    if arguments['flash'] == True:
        add_flash()
    if arguments['exposure'] == True:
        add_speed()
