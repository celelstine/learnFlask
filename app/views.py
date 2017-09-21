from app import app, db, lm, oid, babel
from datetime import datetime
# import flask rending engine
# the package 'g' is used to store global variables that would be access througout the request life time
# the package 
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required

# import package to predict the language a text was written with
from guess_language import guessLanguage

# import flask forms
from .forms import LoginForm, ProfileForm, PostForm, SearchForm

# import the user model
from .models import User, Post

# import configuraton setting
from config import POSTS_PER_PAGE

# import email 
from .emails import follower_notification

# support internalization 
from flask_babel import gettext
from config import LANGUAGES

# this decorator would enable this code to be ran per request
@babel.localeselector
def get_locale():
  # the browser send a property 'accept_languages' in the request header
  # we use the 'best_match' method to get the language in the list of supported languages that best match the client languages
  return 'es' #request.accept_languages.best_match(LANGUAGES.keys())

# this method run before each request
@app.before_request
def before_request():
  g.user = current_user
  if g.user.is_authenticated:
    # update the last_seen column
    g.user.last_seen = datetime.utcnow()
    db.session.add(g.user)
    db.session.commit()
    # make the search form global
    g.search_form = SearchForm()
  # save the current local language for this request
  g.locale = get_locale()

@app.route('/search', methods=['POST'])
@login_required
def search():
  if not g.search_form.validate_on_submit():
    # instead of handling this request here, we redirect because we do not wna the duplicate search on page refresh
    return redirect(url_for('index'))
  return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
  # we use whoosh_search for full text search
  results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
  return render_template('search_results.html',
                           query=query,
                           results=results)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# for pagination
@app.route('/index/<int:page>', methods=['GET', 'POST'])
# protected route
@login_required
def index(page=1):
  # create an instance of the postform
  form = PostForm()
  user = g.user
  if form.validate_on_submit():
    # guess the language that the form we sent in, we language is unknown or invalid return an empty string
    language = guessLanguage(form.post.data)
    if language == 'UNKNOWN' or len(language) > 5:
        language = ''
    post = Post(body=form.post.data,
                timestamp=datetime.utcnow(),
                author=g.user,
                language=language)
    db.session.add(post)
    db.session.commit()
    flash(gettext('Your post is now live!'))
    # we redirect here instead of alow the code move to the 'render_template' line
    # because we want the broswer to render a fresh form without the memory of the previous form data
    # it is a trick to prevent duplicate submission of same data when the user refresh the page
    return redirect(url_for('index'))
  # we use the SQLAlchemy paginate method to return a snippet of the post
  # the last parameter is used to control the returned value when the query return all empty list
  # when it is true, it returns an error else it returns an empty list
  # 'POSTS_PER_PAGE' is stored in config.py 
  # posts = user.followed_posts().paginate(page, POSTS_PER_PAGE, False).items
  # formerly we return the items, but to support page navigation we would return the entire pagination object
  posts = user.followed_posts().paginate(page, POSTS_PER_PAGE, False)

  return render_template('index.html',
                           title='Home',
                           user=user,
                           form=form,
                           posts=posts)

@app.route('/user')
def user1():
  user = {'nickname': 'CeleBobo'}  # fake user
  return render_template('index.html',
                           title='Home',
                           user=user)

@app.route('/posts')
def posts():
  user = g.user  # fake user
  posts = user.followed_posts()
  print(posts, user)
  return render_template("posts.html",
                           title='Home',
                           user=user,
                           posts=posts)

@app.route('/deletePost/<int:id>')
@login_required
def deletePost(id):
  post = Post.query.get(id)
  if post is None:
    flash(gettext('Post not found.'))
    return redirect(url_for('index'))
  if post.author.id != g.user.id:
    flash(gettext('You cannot delete this post.'))
    return redirect(url_for('index'))
  db.session.delete(post)
  db.session.commit()
  flash(('Your post has been deleted.'))
  return redirect(url_for('index'))


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
  user = User.query.filter_by(nickname=nickname).first()
  # print(user.followers.all())
  if user == None:
    flash('User %s not found.' % nickname)
    redirectUrl = '/user/' + nickname
    return redirect(url_for(redirectUrl))
  posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
  print('posts', posts)
  return render_template('user.html',
                           user=user,
                           posts=posts)
                          
# route to follow a user
@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
  user = User.query.filter_by(nickname=nickname).first()
  if user is None:
    flash('User %s not found.' % nickname)
    return redirect(url_for('index'))
  if user == g.user:
    flash('You can\'t follow yourself!')
    return redirect(url_for('user', nickname=nickname))
  u = g.user.follow(user)
  if u is None:
    flash('Cannot follow ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))

  follower_notification(user, g.user)
  db.session.add(u)
  db.session.commit()
  flash('You are now following ' + nickname + '!')
  return redirect(url_for('user', nickname=nickname))

# route to unfollow a user

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
  user = User.query.filter_by(nickname=nickname).first()
  if user is None:
    flash('User %s not found.' % nickname)
    return redirect(url_for('index'))
  if user == g.user:
    flash('You can\'t unfollow yourself!')
    return redirect(url_for('user', nickname=nickname))
  u = g.user.unfollow(user)
  if u is None:
    flash('Cannot unfollow ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))
  db.session.add(u)
  db.session.commit()
  flash('You have stopped following ' + nickname + '.')
  return redirect(url_for('user', nickname=nickname))



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
  form = ProfileForm(g.user.nickname)
  if form.validate_on_submit():
    g.user.nickname = form.nickname.data
    g.user.about_me = form.about_me.data
    db.session.add(g.user)
    db.session.commit()
    flash('Your changes have been saved.')
    return redirect(url_for('profile'))
  else:
    form.nickname.data = g.user.nickname
    form.about_me.data = g.user.about_me
  return render_template('profile.html', form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
# this decorator attach this view to the Flask-OpenID login handler
@oid.loginhandler
# we attach the wft form class to the template class
def login():
  # redirect the user to the index page when the user is authenticated
  if g.user is not None and g.user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    # store the remember_me in the session, this is not the db session, the fucntion recieves the openId given to the user and the data we want after successful authenticatio
    session['remember_me'] = form.remember_me.data 
    # we return a call to flask_openID authenticate the user
    return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    flash('Login requested for OpenID="%s", remember_me=%s' %
            (form.openid.data, str(form.remember_me.data)))
    return redirect('/index')
  return render_template('login.html', 
                          title='Sign In',
                          providers=app.config['OPENID_PROVIDERS'],
                          form=form)
          
# method to get a user by id, this method is used by flask_login 
# we register this method to the flask_login user_loader method
@lm.user_loader
def load_user(id):
  # we convert the user id to integer because flask_login stores it as string
  return User.query.get(int(id))

# flask_openID calls this method after succesful authentication
@oid.after_login
def after_login(resp):
  # redirect user when email does not exist
  if resp.email is None or resp.email == "":
    flash(gettext('Invalid login. Please try again.'))
    return redirect(url_for('login'))
  # query to get the user
  user = User.query.filter_by(email=resp.email).first()
  if user is None:
    nickname = resp.nickname
    if nickname is None or nickname == "":
      nickname = resp.email.split('@')[0]
    # remove possible hacking characters from the input
    nickname = User.make_valid_nickname(nickname)
    # get a unique nickname for user
    nickname = User.make_unique_nickname(nickname)
    user = User(nickname=nickname, email=resp.email)

    # make the user follow him/herself
    db.session.add(user.follow(user))

    db.session.add(user)
    db.session.commit()
  remember_me = False
  if 'remember_me' in session:
    remember_me = session['remember_me']
    session.pop('remember_me', None)
  # the flask login_user logs the user in 
  login_user(user, remember = remember_me)
  return redirect(request.args.get('next') or url_for('index'))

# http error handling middleware
@app.errorhandler(404)
def not_found_error(error):
  return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
  db.session.rollback()
  return render_template('500.html'), 500

# this package is used to get the excution log of flask queries
from flask_sqlalchemy import get_debug_queries
from config import DATABASE_QUERY_TIMEOUT

@app.after_request
def after_request(response):
  # we loop through each query for this request and check if they exceed the minimum threshold
  for query in get_debug_queries():
    if query.duration >= DATABASE_QUERY_TIMEOUT:
      app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
  return response