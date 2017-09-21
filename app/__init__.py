"""
.. module:: useful_1
   :platform: Unix, Windows
   :synopsis: A useful module indeed.

.. moduleauthor:: Andrew Carter <andrew@invalid.com>


"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# we create an instance of a flask application
app = Flask(__name__)

# link the app to the configuration file
app.config.from_object('config')
# create a db for  app
db = SQLAlchemy(app)

import os
from flask_login import LoginManager
from flask_openid import OpenID

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

# import flask_babel for internationalization and localization
from flask_babel import Babel
babel = Babel(app)

# LoginManager is used to  manage the logged in user state
# OpenID is user for authentcation, it require a pointer to a temporary folder to store files
lm = LoginManager()
lm.init_app(app)
# point the login_view to the login view (lol)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))

# we import the views module of the application,
# this import is placed after creating the app because the view modules need the app variable
from app import views, models

# setup error logging , mail would be sent to admin and a log file os also maintained
if not app.debug:
  import logging
  from logging.handlers import SMTPHandler, RotatingFileHandler
  # for mail logging
  # run the code in your terminal to use the python stmp --> python -m smtpd -n -c DebuggingServer localhost:25
  credentials = None
  if MAIL_USERNAME or MAIL_PASSWORD:
      credentials = (MAIL_USERNAME, MAIL_PASSWORD)
  # create the mail handle with the credentail, 
  mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
  # send email when an ERROR occurs
  mail_handler.setLevel(logging.ERROR)
  app.logger.addHandler(mail_handler)

  # for file logging
  # create a file handle with a 'RotatingFileHandler' to remove old linnes whena new line is added 
  # and the file has reach the max size which we set as 2mb here
  # the handler would tracker the last 20 log
  file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 2 * 1024 * 1024, 20)
  # we use the 'setFormatter' to format the message 
  file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
  # we lower the logging level to accomodate more log info
  app.logger.setLevel(logging.INFO)
  file_handler.setLevel(logging.INFO)
  # attach the 'file_handler' to the app logger
  app.logger.addHandler(file_handler)
  # add a sample log to testing 
  app.logger.info('Cele test log startup')

# initialize the mail server
from flask_mail import Mail
mail = Mail(app)

# make the moment transformation markup accessible globally to all templates
from .momentjs import momentjs
app.jinja_env.globals['momentjs'] = momentjs

# we want to set and translate the message shown to a user when he is nont log in
# we use lazy_gettext instead of 'gettext' since we want this translation only when the text would be shown
from flask_babel import lazy_gettext
lm.login_message = lazy_gettext('Please log in to access this page.')


# we want to override the default flask user session which is a complex json object to enable from flask.json import JSONEncoder lazy_gettext

class CustomJSONEncoder(JSONEncoder):
  """This class adds support for lazy translation texts to Flask's
  JSON encoder. This is necessary when flashing translated texts."""
  def default(self, obj):
    from speaklater import is_lazy_string
    if is_lazy_string(obj):
      try:
        return unicode(obj)  # python 2
      except NameError:
        return str(obj)  # python 3
    return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

def public_fn_with_googley_docstring(name, state=None):
    """This function does something.

    Args:
       name (str):  The name to use.

    Kwargs:
       state (bool): Current state to be in.

    Returns:
       int.  The return code::

          0 -- Success!
          1 -- No good.
          2 -- Try again.

    Raises:
       AttributeError, KeyError

    A really great idea.  A way you might use me is

    >>> print public_fn_with_googley_docstring(name='foo', state=None)
    0

    BTW, this always returns 0.  **NEVER** use with :class:`MyPublicClass`.

    """
    return 0