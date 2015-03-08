import cgi
import os
import jinja2
import webapp2
import uuid
import RequestSignature
import TemperatureDataModel
import datetime
from google.appengine.ext import ndb

template_env = jinja2.Environment(
                            loader=jinja2.FileSystemLoader(os.getcwd()))

class Index(webapp2.RequestHandler):
    def get(self):
        self.response.write('hello')

class ExportLast(webapp2.RequestHandler):
    def get(self):
        # get device id
        device_id = self.request.get('did')
        if (device_id == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter device id did')
            return

        temperature = TemperatureDataModel.Temperature.temperatures_last( \
                                            ndb.Key("Device", device_id))
        
        if temperature == None:
            self.error(400)
            self.response.write('ERROR: wrong device id')
            return

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("{0},{1}\n".format(temperature.timestamp.strftime('%Y-%m-%d %H:%M:%S'), \
                                                  temperature.temperature, \
                                                  ))        

class ExportCSV(webapp2.RequestHandler):
    def get(self):
        # get device id
        device_id = self.request.get('did')
        if (device_id == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter device id did')
            return

        start = self.request.get('start')
        end = self.request.get('end')
        hours = self.request.get('hours')

        if start != '' and end != '':
            try:
                start = datetime.datetime.strptime(start, '%Y-%m-%d')
                end = datetime.datetime.strptime(end, '%Y-%m-%d')
            except ValueError:
                self.error(400)
                self.response.write('ERROR: wrong dates')
                return

            temperature_list = TemperatureDataModel.Temperature.temperatures_by_device_date_filter( \
                                            ndb.Key("Device", device_id), \
                                            start, \
                                            end)
        else:
            temperature_list = TemperatureDataModel.Temperature.temperatures_by_device( \
                                            ndb.Key("Device", device_id))

        self.response.headers['Content-Type'] = 'text/plain'
        for temperature_data in temperature_list:
            self.response.write("{0},{1}\n".format(temperature_data.timestamp.strftime('%Y-%m-%d %H:%M:%S'), \
                                                  temperature_data.temperature, \
                                                  ))        

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

class Chart(webapp2.RequestHandler):
    def get(self):
        # get device id
        device_id = self.request.get('did')
        if (device_id == ''):
            self.error(400)
            self.response.write('ERROR: missing parameter device id did')
            return

        template = template_env.get_template('chart.html')

        temperature_list = TemperatureDataModel.Temperature.temperatures_by_device_since( \
                                            ndb.Key("Device", device_id), 24)

        chart_data = ''
        for temperature_data in temperature_list:
            chart_data += "['{0}',{1}],\n".format(temperature_data.timestamp.strftime('%Y-%m-%d %H:%M'), \
                                                  temperature_data.temperature, \
                                                  )

        self.response.out.write(
            template.render({'chart_data' : chart_data}))

application = webapp2.WSGIApplication([
    ('/', Index),
    ('/save', Save),
    ('/export/csv', ExportCSV),
    ('/export/chart', Chart),
    ('/export/last', ExportLast),
], debug=True)
