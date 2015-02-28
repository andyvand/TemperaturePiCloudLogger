import cgi
import os
import jinja2
import webapp2
import uuid
import RequestSignature
import TemperatureDataModel
from google.appengine.ext import ndb


template_env = jinja2.Environment(
                            loader=jinja2.FileSystemLoader(os.getcwd()))

class Index(webapp2.RequestHandler):
    def get(self):
        self.response.write('hello')

class ExportCSV(webapp2.RequestHandler):
    def get(self):
        # get device id
        device_id = self.request.get('did')
        if (device_id == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter device id did')
            return
        
        temperature_list = TemperatureDataModel.Temperature.temperatures_by_device( \
                                            ndb.Key("Device", device_id))

        self.response.headers['Content-Type'] = 'text/plain'
        for temperature_data in temperature_list:
            self.response.write("{0},{1}\n".format( \
                                                  temperature_data.temperature, \
                                                  temperature_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')))

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
        
        
        
class Save(webapp2.RequestHandler):
    def get(self):
        # get device id
        device_id = self.request.get('did')
        if (device_id == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter device id did')
            return

        # get device secret
        device_list = TemperatureDataModel.Device.query(TemperatureDataModel.Device.device_id == device_id).fetch()
        if len(device_list) != 1:
            self.error(400)
            self.response.write('ERROR: wrong device id')
            return
        
        device = device_list[0]
        
        # get temperature
        temperature_param = self.request.get('t')
        if (temperature_param == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter temperature t')
            return
        
        try:
            temperature = float(temperature_param)
        except ValueError:
            self.error(400)
            self.response.write('ERROR: temperature t is not number')
            return
        

        # get signature
        signature = self.request.get('sig')
        if (signature == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter signature sig')
            return

        # check signature
        if (not RequestSignature.RequestSignature.check([device_id, temperature_param], device.secret, signature)):
            self.error(401)
            self.response.write('ERROR: wrong signature')
            return
        
        temperature_data = TemperatureDataModel.Temperature(parent = ndb.Key("Device", device_id),
                                                            temperature = temperature)
        
        temperature_data.put()

application = webapp2.WSGIApplication([
    ('/', Index),
    ('/save', Save),
    ('/export/csv', ExportCSV),
    ('/add/device', AddDevice),
], debug=True)