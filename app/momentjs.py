from jinja2 import Markup

# class to encapsulate moment date feature
class momentjs(object):
  def __init__(self, timestamp):
    self.timestamp = timestamp

  # method to render the moment transformation to the browser
  def render(self, format):
    return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

  def format(self, fmt):
    return self.render("format(\"%s\")" % fmt)

  def calendar(self):
    return self.render("calendar()")

  def fromNow(self):
    return self.render("fromNow()")