# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import re
from lxml import etree
import pymongo
from pymongo import MongoClient
from datetime import datetime
import calendar
import requests
import yaml
import logging

def time_to_timestamp(time):
    dt = datetime.strptime(time, "%H%M%S")
    dt_now = datetime.now()
    dt = dt.replace(year=dt_now.year, month=dt_now.month, day=dt_now.day)

    return calendar.timegm(dt.utctimetuple())

def decode_body(body_content):
    tree = etree.fromstring(body_content)
    dev_id = tree.find('{http://uri.actility.com/lora}DevEUI').text
    data_str = tree.find('{http://uri.actility.com/lora}payload_hex').text.decode("hex")

    return dev_id, data_str

def parse_data(data_str):
    data_pattern = ".*;.*;.*"
    _data = {}
    if re.match(data_pattern, data_str):
        data = data_str.split(';')
        _data['time'] = data[0]
        _data['coordinate'] = []
        _data['coordinate'].append(float(data[1]))
        _data['coordinate'].append(float(data[2]))
        _data['timestamp'] = time_to_timestamp(data[0])
        return _data

def store_in_db(dev_id, gps_data):
    if collection:
        collection.update({"properties.dev_id": dev_id},{"$push": {"geometry.coordinates": gps_data['coordinate']}})
        collection.update({"properties.dev_id": dev_id},{"$push": {"properties.time": gps_data['timestamp']}})

def push_to_livesite(dev_id, gps_data):
    _data = {}
    _data['device_id'] = dev_id
    _data['new_position'] = gps_data['coordinate']
    _data['time'] = gps_data['timestamp']
    print _data
    live_api_url = "http://84.39.44.100:8080"
    if live_api_url:
        url = live_api_url + "/api/update"
        requests.put(url=url, data=_data) 

def log_result(dev_id, gps_data):
    logger.info("DEVICE ID : %s CORD :  %s,%s TIME: %s", dev_id, gps_data['coordinate'][0], gps_data['coordinate'][1], gps_data['time'])

def init_database(url, port):
    client = MongoClient(url, port)
    db = client.raid

    return db.trace

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("LoRa API for 'ENSSAT Raid Aventure' !")

    def post(self):
        logger.debug(self.request.body)
        dev_id, data_str = decode_body(self.request.body)
        gps_data = parse_data(data_str)

        if gps_data:
            log_result(dev_id, gps_data)
            #store_in_db(dev_id, gps_data)
            #push_to_livesite(dev_id, gps_data)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('LoRa API')
    logger.setLevel(logging.DEBUG)
    app = make_app()
    app.listen(8080)
    global collection 
    collection = init_database('valentin-boucher.fr', 27017)
    tornado.ioloop.IOLoop.current().start()