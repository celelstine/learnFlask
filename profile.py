# this file contains code for code profile: which is to test the excution time of the code base
#!flask/bin/python
from werkzeug.contrib.profiler import ProfilerMiddleware
from app import app

app.config['PROFILE'] = True
# this line wouls show the 30 most expensive functions per each request
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.run(debug = True)