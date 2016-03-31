# coding: utf8
import tornado.ioloop
import tornado.web

from tracking_tools import *


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("LoRa API for 'ENSSAT Raid Aventure' !")

    def post(self):
        logger.debug(self.request.body)
        dev_id, data_str = decode_body(self.request.body)
        gps_data = parse_data(data_str)

        if gps_data:
            log_result(dev_id, gps_data, logger)
            #store_in_db(dev_id, collection, gps_data)
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