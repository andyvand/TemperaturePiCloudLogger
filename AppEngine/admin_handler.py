import cgi
import os
import jinja2
import webapp2
import uuid
import TemperatureDataModel
from google.appengine.ext import ndb


template_env = jinja2.Environment(
                            loader=jinja2.FileSystemLoader(os.getcwd()))

class AddDevice(webapp2.RequestHandler):
    def get(self):
        template = template_env.get_template('add_device_template.html')
        self.response.out.write(
            template.render())
    
    def post(self):
        device_id = self.request.get('did')
        if (device_id == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter Device ID')
            return

        description = self.request.get('description')
        
        secret = str(uuid.uuid1())
        
        device = TemperatureDataModel.Device()
        device.device_id = device_id
        device.description = description
        device.secret = secret
        
        device.put()
        self.response.write(secret)

application = webapp2.WSGIApplication([
    ('/setup/add-device', AddDevice),
], debug=True)
