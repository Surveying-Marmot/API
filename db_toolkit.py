""" Database toolkit for photo scout

Usage:
  db_toolkit.py create
  db_toolkit.py migrate
  db_toolkit.py upgrade
  db_toolkit.py downgrade
  db_toolkit.py drop
  db_toolkit.py code
  db_toolkit.py list
  db_toolkit.py (-h | --help)
  db_toolkit.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

import os.path
import imp
from docopt import docopt
from migrate.versioning import api
from app.models import BetaCode
import app
from app import db
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
import random, string

def create_db():
    """ Create the databases needed """
    db.create_all()
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

    # Get the first beta code
    code = raw_input("Enter the first beta code:")
    beta_code = BetaCode(code=code)
    db.session.add(beta_code)
    db.session.commit()

def migrate_db():
    """ Migrate an existing database to a new format """
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    exec(old_model, tmp_module.__dict__)
    script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
    open(migration, "wt").write(script)
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('New migration saved as ' + migration)
    print('Current database version: ' + str(v))

def upgrade_db():
    """ Upgrade the database to the next version """
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version: ' + str(v))

def downgrade_db():
    """ Downgrade the database to the previous version """
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version: ' + str(v))

def delete_db():
    """ Delete the whole database """
    db.drop_all()

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def add_beta_code():
    # Get the first beta code
    number = raw_input("Number of codes to generate:")
    for i in range(0, int(number)):
        code = randomword(16)
        beta_code = BetaCode(code=code)
        db.session.add(beta_code)
    db.session.commit()

def list_beta_code():
    codes = BetaCode.query.all()

    for code in codes:
        print(code)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    if arguments['create'] == True:
        create_db()
    elif arguments['migrate'] == True:
        migrate_db()
    elif arguments['upgrade'] == True:
        upgrade_db()
    elif arguments['downgrade'] == True:
        downgrade_db()
    elif arguments['drop'] == True:
        delete_db()
    elif arguments['code'] == True:
        add_beta_code()
    elif arguments['list'] == True:
        list_beta_code()
