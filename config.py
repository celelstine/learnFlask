# the code below is the configuration for flask wtform packagewhich processes form request
WTF_CSRF_ENABLED = True
SECRET_KEY = 'This-flask-make-sense-eh222222'

# list of openID
OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

# SQLAlchemy configuration for sqlite
import os
# get the absolute path of this file
basedir = os.path.abspath(os.path.dirname(__file__))
 # config the address to the database file and the folder to store migrations
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# for error logging
# mail server settings
# the commented settign id for localhost
  # MAIL_SERVER = 'localhost'
  # MAIL_PORT = 25
  # MAIL_USERNAME = 'okorocelestine@gmail.com'
  # MAIL_PASSWORD = 'nkemjika'
# setting for gmail
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'okorocelestine@gmail.com' #os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = 'nkemjika' #os.environ.get('MAIL_PASSWORD')
print('MAIL_USERNAME', MAIL_USERNAME)
# administrator list
ADMINS = ['okorocelestine@gmail.com']

# pagination
POSTS_PER_PAGE = 3

# configure db for WHOOSH full text search
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

# -*- coding: utf-8 -*-
# the line above is a decorator that tell python to use utf-8 which support non-english characters like 'ñ' instead on ASCII
# available languages
LANGUAGES = {
  'en': 'English',
  'es': 'Español'
}

# for profiling
SQLALCHEMY_RECORD_QUERIES = True

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5