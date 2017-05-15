from urllib.request import Request, urlopen
from abc import abstractmethod

from nameko.extensions import SharedExtension

from nameko_zipkin.constants import *


class IHandler:
    def start(self):
        pass

    def stop(self):
        pass

    @abstractmethod
    def handle(self, encoded_span):
        pass


class HttpHandler(IHandler):
    def __init__(self, url):
        self.url = url

    def handle(self, encoded_span):
        body = b'\x0c\x00\x00\x00\x01' + encoded_span
        request = Request(self.url, body, {'Content-Type': 'application/x-thrift'}, method='POST')
        urlopen(request)


class Transport(SharedExtension):
    def __init__(self):
        self._handler = None

    def setup(self):
        config = self.container.config[ZIPKIN_CONFIG_SECTION]
        handler_cls = globals()[config[HANDLER_KEY]]
        handler_params = config[HANDLER_PARAMS_KEY]
        self._handler = handler_cls(**handler_params)

    def start(self):
        self._handler.start()

    def stop(self):
        self._handler.stop()

    def handle(self, encoded_span):
        self._handler.handle(encoded_span)
