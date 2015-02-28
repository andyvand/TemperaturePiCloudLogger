import glob
import time
import urllib2
import RequestSignature

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

secret = 'cbc07838-bf40-11e4-9d58-b5a7297fd676'
device_id = 'k-palecku-1'
url='http://raspi-temperature-01.appspot.com/save?did={0}&t={1}&sig={2}'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    
    # check CRC
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
    
    lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
    
    temperature = float(temp_string) / 1000.0
    
    return temperature


temperature = str(read_temp())
signature = RequestSignature.RequestSignature.sign([device_id, temperature], secret)
response = urllib2.urlopen(url.format(device_id, temperature, signature))
print temperature
