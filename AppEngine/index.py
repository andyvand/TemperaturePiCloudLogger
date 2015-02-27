import cgi
import webapp2
import RequestSignature
import TemperatureDataModel

class Index(webapp2.RequestHandler):
    def get(self):
        self.response.write('hello')

class Save(webapp2.RequestHandler):
    def get(self):
        # get temperature
        temperature = self.request.get('t')
        if (temperature == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter temperature t')
            return
        
        # get device id
        device_id = self.request.get('did')
        if (device_id == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter device id did')
            return
        
        # get signature
        signature = self.request.get('sig')
        if (signature == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter signature sig')
            return

        self.response.write(temperature)

application = webapp2.WSGIApplication([
    ('/', Index),
    ('/save', Save),
], debug=True)