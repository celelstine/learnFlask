from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length

# class for login
class LoginForm(FlaskForm):
  openid = StringField('openid', validators=[DataRequired()])
  remember_me = BooleanField('remember_me', default=False)

# class for edit profile
class ProfileForm(FlaskForm):
  nickname = StringField('nickname', validators=[DataRequired()])
  about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
  def __init__(self, original_nickname, *args, **kwargs):
    FlaskForm.__init__(self, *args, **kwargs)
    self.original_nickname = original_nickname

  def validate(self):
    if not Form.validate(self):
      return False

    # return true when the user did not change her nickname
    if self.nickname.data == self.original_nickname:
      return True

    # disallow non-alphanumeric characters
    if self.nickname.data != User.make_valid_nickname(self.nickname.data):
      self.nickname.errors.append(gettext('This nickname has invalid characters. Please use letters, numbers, dots and underscores only.'))
      return False

    user = User.query.filter_by(nickname=self.nickname.data).first()
    if user is not None:
      self.nickname.errors.append(gettext('This nickname is already in use. Please choose another one.'))
      return False
    return True

# class to post a blog
class PostForm(FlaskForm):
  post = StringField('post', validators=[DataRequired()])

# class for the search form
class SearchForm(FlaskForm):
  search = StringField('search', validators=[DataRequired()])