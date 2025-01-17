#! /usr/bin/env python3

import json
import configparser
import logging

from time import sleep
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

logger.info('Loading Pynq overlay, this might take a while...')
from pynq.overlays.base import BaseOverlay
overlay = BaseOverlay('base.bit')

def led_sequence():
    # Flash the LEDs to indicate the server has started up
    leds = overlay.leds

    leds[0:4].off()

    for i, led in enumerate(leds):
        if i > 0:
            leds[i-1].off()
        led.on()
        sleep(0.2)

    leds[0:4].off()

    for _ in range(8):
        leds[0:4].toggle()
        sleep(0.4)

    leds[0:4].off()

class ServerHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def set_leds(self, leds_desired_state):
        leds = overlay.leds

        if len(leds_desired_state) != leds.length:
            bad_request = HTTPStatus.BAD_REQUEST
            self.send_error(bad_request.value, bad_request.phrase, f"Expected exactly 4 values in the leds array, got {len(leds_desired_state)}")
            return

        mask = 0b1111
        try:
            value = int(''.join(str(i) for i in leds_desired_state), 2)
        except Exception as e:
            error = HTTPStatus.INTERNAL_SERVER_ERROR
            self.send_error(error.value, error.phrase, f"Something went wrong decoding the leds array: {type(e)}")
            return
        leds.write(value, mask)

    def do_GET(self):
        leds = overlay.leds
        data = {}
        data['leds'] = list(map(int, f"{leds[0:4].read():04b}"))

        self._set_headers('application/json')
        self.wfile.write(f"{json.dumps(data)}\n".encode())

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        content_length = int(self.headers['Content-Length'])
        try:
            data = json.loads(self.rfile.read(content_length))
        except json.JSONDecodeError as e:
            bad_request = HTTPStatus.BAD_REQUEST
            self.send_error(bad_request.value, bad_request.phrase, f"{e.msg}")
            return

        self.set_leds(data['leds'])

        self.send_response(HTTPStatus.OK.value)

if __name__ == '__main__':
    # Parse the /etc/leds-server.conf file
    etc_leds_server_path = '/etc/leds-server.conf'
    logger.info(f"Reading {etc_leds_server_path}...")
    config = configparser.ConfigParser()
    config.read(etc_leds_server_path)
    address = config['server']['address']
    port = int(config['server']['port'])

    # Prepare the HTTP server
    server_address = (address, port)
    request_handler = ServerHandler
    server = HTTPServer(server_address, request_handler)

    # Notify the user that we're staring
    logger.info('Doing little LED sequence...')
    led_sequence()

    # Start the HTTP server
    logger.info('Starting HTTP LED server...')
    server.serve_forever()
