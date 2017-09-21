from flask_mail import Message
from flask import render_template
from config import ADMINS
# the package below is use for asynchronous process
from .decorators import async

from app import app
from flask_mail import Mail
mail = Mail(app)
# method to send mail using flask_mail
def send_email(subject, sender, recipients, text_body, html_body):
  '''
    Mayawo say hi, abi

    args:
      subject (str):  The name to use.
      sender (str):  The name to use.
      recipients (str):  The name to use.
      text_body (str):  The name to use.
      html_body (str):  The name to use.
  '''
  msg = Message(subject, sender=sender, recipients=recipients)
  msg.body = text_body
  msg.html = html_body
  # create a new thread to send the mail synchronously
  send_async_email(app, msg)

# asyn functon to send mail
def send_async_email(app, msg):
  with app.app_context():
    mail.send(msg)

# method to send user mail when a user follow her
def follower_notification(followed, follower):
  send_email("[microblog] %s is now following you!" % follower.nickname,
               ADMINS[0],
               [followed.email],
               render_template("follower_email.txt", 
                              user=followed, follower=follower),
               render_template("follower_email.html", 
                               user=followed, follower=follower))