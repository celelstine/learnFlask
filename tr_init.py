#!flask/bin/python
# this is an encapsulation of the code to add a new langauge to flask_babel
# it should be run as ./tr_init.py <langugae>
import os
import sys
if sys.platform == 'win32':
  pybabel = 'flask\\Scripts\\pybabel'
else:
  pybabel = 'flask/bin/pybabel'
if len(sys.argv) != 2:
  print "usage: tr_init <language-code>"
  sys.exit(1)
os.system(pybabel + ' extract -F babel.cfg -k lazy_gettext -o messages.pot app')
os.system(pybabel + ' init -i messages.pot -d app/translations -l ' + sys.argv[1])
os.unlink('messages.pot')