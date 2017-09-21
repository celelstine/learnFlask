from app import db, app
from hashlib import md5
import sys


# conditional import for whoosh , only enabled for python2
if sys.version_info >= (3, 0):
  enable_search = False
else:
  enable_search = True
  import flask_whooshalchemy as whooshalchemy

# auxilliary table for follower relationship
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# a model for user
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nickname = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  # attach a post to users
  posts = db.relationship('Post',
                          backref='author',
                          lazy='dynamic')
  about_me = db.Column(db.String(140))
  last_seen = db.Column(db.DateTime)
  # attach a list of followers
  # 'secondary' indicates the association table that is used for this relationship.
  # 'primaryjoin' indicates the condition that links the left side entity (the follower user) with the association table
  # 'secondaryjoin' indicates the condition that links the right side entity (the followed user) with the association table.
  # 'backref' defines how this relationship will be accessed from the right side entity.
  followed = db.relationship('User', 
                              secondary=followers, 
                              primaryjoin=(followers.c.follower_id == id), 
                              secondaryjoin=(followers.c.followed_id == id), 
                              backref=db.backref('followers', lazy='dynamic'), 
                              lazy='dynamic')

  # we made this  a static method, since the object does not exist at this point
  @staticmethod
  def make_unique_nickname(nickname):
    if User.query.filter_by(nickname=nickname).first() is None:
      return nickname
    version = 2
    while True:
      new_nickname = nickname + str(version)
      if User.query.filter_by(nickname=new_nickname).first() is None:
        break
      version += 1
    return new_nickname

  # the following methods are requirement for flask_login
  @property
  def is_authenticated(self):
    return True

  @property
  def is_active(self):
    return True

  @property
  def is_anonymous(self):
    return False

  def get_id(self):
    try:
      return unicode(self.id)  # python 2
    except NameError:
      return str(self.id)  # python 3
  # the required method for flask_login ends here

  # override the string print method
  def __repr__(self):
    return '<User %r>' % (self.nickname)

  # method to get avarter
  def avatar(self, size):
    return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

  # method for follwoers
  def follow(self, user):
    if not self.is_following(user):
      self.followed.append(user)
      return self

  def unfollow(self, user):
    if self.is_following(user):
      self.followed.remove(user)
      return self

  def is_following(self, user):
    return self.followed.filter(followers.c.followed_id == user.id).count() > 0

  # get the posts by a users's followed
  def followed_posts(self):
    print('check the user id', self.id)
    return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

  # method to remove non alphenumeric characters from the client nickname
  @staticmethod
  def make_valid_nickname(nickname):
    return re.sub('[^a-zA-Z0-9_\.]', '', nickname)


# model for blog post
class Post(db.Model):
  # for full text search with WHOOSH
  # this is a array for the fields that we want to included in the search
  __searchable__ = ['body']
  id = db.Column(db.Integer, primary_key = True)
  body = db.Column(db.String(140))
  timestamp = db.Column(db.DateTime)
  # a link between user model and blog post
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  # column to store the language that a post was written with
  language = db.Column(db.String(5))

  def __repr__(self):
    return '<Post %r>' % (self.body)

  # we intialize whooshalchemy with the app and the model
  if enable_search:
    whooshalchemy.whoosh_index(app, Post)