import atexit
import json
import logging
import os

from twisted.internet import reactor, protocol
from twisted.protocols import basic

from twisted.web import server, resource, client

logger = logging.getLogger('password_db.common')


class Halt(Exception):
    pass


class HTTPServer(object, resource.Resource):
    isLeaf = True

    def __init__(self, processor, args):
        self.processor = processor
        self.args = args

    def render_GET(self, request):
        return ('{"success": false, "message": "GET not supported.'
                ' Try POSTing instead."}\n')

    def render_POST(self, request):
        processor_instance = self.processor(request, self.args)
        processor_instance.processRaw()
        return server.NOT_DONE_YET

class PayloadProcessor(object):
    request_count = 0

    def __init__(self, request):
        PayloadProcessor.request_count += 1
        self.request_id = PayloadProcessor.request_count
        self.request = request

    def processRaw(self):
        raw_data = self.request.content.read()
        self.log_info('Received payload: %r', raw_data)

        try:
            parsed = json.loads(raw_data)
        except ValueError as e:
            self.respondWithMessage('Could not parse message: %s' % e)
            return

        try:
            self.process(parsed)
        except Halt:
            pass

    # API method
    def process(self, data):
        raise NotImplementedError

    # Utility methods
    def getArg(self, data, name):
        try:
            return data[name]
        except KeyError:
            self.respondWithMessage('Missing required param: %s' % name)
            raise Halt()

    def respondWithMessage(self, message):
        response = {
            'success' : False,
            'message' : message
            }
        self.respond(response)

    def respond(self, response):
        if self.request.notifyFinish():
            self.log_error("Request already finished!")
        formatted = json.dumps(response) + '\n'
        self.log_info('Responding with: %r', formatted)
        self.request.write(formatted)
        self.request.finish()

    def log_info(self, *args):
        self.log('info', *args)

    def log_error(self, *args):
        self.log('error', *args)

    def log(self, level, msg, *args):
        # Make this should actually be handled by a formatter.
        client = self.request.client
        try:
            host = client.host
            port = client.port
        except AttributeError:
            prefix = '[%r:%d] '  % (client, self.request_id)
        else:
            prefix = '[%s:%d:%d] '  % (host, port, self.request_id)
        method = getattr(logger, level)
        interpolated = msg % args
        method(prefix + interpolated)

def chunkPassword(chunk_count, password, request=None):
    # Equivalent to ceil(password_length / chunk_count)
    chunk_size = (len(password) + chunk_count - 1) / chunk_count

    chunks = []
    for i in xrange(0, len(password), chunk_size):
        chunks.append(password[i:i+chunk_size])

    while len(chunks) < chunk_count:
        chunks.append('')

    msg = 'Split length %d password into %d chunks of size about %d: %r'
    args = [len(password), chunk_count, chunk_size, chunks]
    if request:
        request.log_info(msg, *args)
    else:
        logger.info(msg, *args)

    return chunks

def isUnix(spec):
    return spec.startswith('unix:')

def parseHost(host):
    host, port = host.split(':')
    port = int(port)
    return host, port

def parseUnix(unix):
    path = unix[len('unix:'):]
    return path

def makeRequest(address_spec, data, callback, errback):
    # Change the signature of the errback
    def wrapper(error):
        errback(address_spec, error)

    host, port = address_spec
    factory = client.HTTPClientFactory('/',
                                       agent='PasswordChunker',
                                       method='POST',
                                       postdata=json.dumps(data))
    factory.deferred.addCallback(callback)
    factory.deferred.addErrback(wrapper)
    reactor.connectTCP(host, port, factory)

def listenTCP(address_spec, http_server):
    host, port = address_spec
    site = server.Site(http_server)
    reactor.listenTCP(port, site, 50, host)

def cleanupSocket(path):
    try:
        os.remove(path)
    except OSError:
        pass

def listenUNIX(path, http_server):
    site = server.Site(http_server)
    reactor.listenUNIX(path, site, 50)
    atexit.register(cleanupSocket, path)
