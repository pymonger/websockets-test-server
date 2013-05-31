import sys

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol


class PubSubServer1(WampServerProtocol):
    def onSessionOpen(self):
        self.registerForPubSub("http://example.com/simple")
        self.registerForPubSub("http://example.com/event#", True)

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
    factory = WampServerFactory("ws://0.0.0.0:9000", debugWamp = debug)
    factory.protocol = PubSubServer1
    factory.setProtocolOptions(allowHixie76 = True)
    listenWS(factory)
    reactor.run()
