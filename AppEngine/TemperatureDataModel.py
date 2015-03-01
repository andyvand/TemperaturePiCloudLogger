from google.appengine.ext import ndb

class Temperature(ndb.Model):
    temperature = ndb.FloatProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def temperatures_by_device(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(cls.timestamp)
    
    @classmethod
    def temperatures_by_device_date_filter(cls, ancestor_key, start, end):
        return cls.query(ancestor=ancestor_key). \
            filter(ndb.GenericProperty('timestamp') >= start). \
            filter(ndb.GenericProperty('timestamp') <= end). \
            order(cls.timestamp)
    
class Device(ndb.Model):
    device_id = ndb.StringProperty(required=True)
    secret = ndb.StringProperty(required=True)
    desciption = ndb.TextProperty()
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()