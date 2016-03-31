# coding: utf8
import re
from pymongo import MongoClient
from datetime import datetime
import calendar
import requests
import logging
from lxml import etree


def time_to_timestamp(time):
    dt = datetime.strptime(time, "%H%M%S")
    dt_now = datetime.now()
    dt = dt.replace(year=dt_now.year, month=dt_now.month, day=dt_now.day)

    return calendar.timegm(dt.utctimetuple())


def decode_body(body_content):
    tree = etree.fromstring(body_content)
    dev_id = tree.find('{http://uri.actility.com/lora}DevEUI').text
    data_str = tree.find(
        '{http://uri.actility.com/lora}payload_hex').text.decode("hex")
    rssi = tree.find('{http://uri.actility.com/lora}LrrRSSI').text
    snr = tree.find('{http://uri.actility.com/lora}LrrSNR').text

    return dev_id, data_str, rssi, snr


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


def store_in_db(dev_id, collection, gps_data):
    if collection:
        collection.update({"properties.dev_id": dev_id}, {
                          "$push": {"geometry.coordinates": gps_data['coordinate']}})
        collection.update({"properties.dev_id": dev_id}, {
                          "$push": {"properties.time": gps_data['timestamp']}})


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


def log_result(dev_id, gps_data, logger):
    logger.info("DEVICE ID: %s CORD:  %s,%s TIME: %s RSSI: %s SNR: %s ", dev_id, gps_data['coordinate'][
                0], gps_data['coordinate'][1], gps_data['time'], gps_data['rssi'], gps_data['snr'])


def init_database(url, port):
    client = MongoClient(url, port)
    db = client.raid

    return db.trace
