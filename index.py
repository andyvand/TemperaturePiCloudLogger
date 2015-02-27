import cgi
from google.appengine.api import users
import webapp2


class Index(webapp2.RequestHandler):
    def get(self):
        self.response.write('hello')

class Save(webapp2.RequestHandler):
    def get(self):
        self.response.write(cgi.escape(self.request.get('t')))


application = webapp2.WSGIApplication([
    ('/', Index),
    ('/save', Save),
], debug=True)