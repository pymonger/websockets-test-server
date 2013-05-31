import sys, json, time

import pika
from pika import exceptions
from pika.adapters import twisted_connection

from twisted.python import log
from twisted.internet import reactor, defer, protocol, task

from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol


class PikaConsumer:
    def __init__(self, factory):
        self.factory = factory

    @defer.inlineCallbacks
    def run(self, connection):
        channel = yield connection.channel()
        queue = yield channel.queue_declare(queue='job_status_log', durable=True)
        yield channel.basic_qos(prefetch_count=1)
        queue_object, consumer_tag = yield channel.basic_consume(queue='job_status_log',no_ack=False)
        l = task.LoopingCall(self.read, queue_object)
        time.sleep(5)
        l.start(0.01)
    
    @defer.inlineCallbacks
    def read(self, queue_object):
        ch,method,properties,body = yield queue_object.get()
        if body:
            print body
        self.factory.dispatch("http://example.com/simple", json.loads(body))
        yield ch.basic_ack(delivery_tag=method.delivery_tag)
    
    
class PubSubServer(WampServerProtocol):
    def onSessionOpen(self):
        # only allow clients to subscribe; this server does the publishing
        self.registerForPubSub("http://example.com/simple", pubsub=WampServerProtocol.SUBSCRIBE)
        self.registerForPubSub("http://example.com/event#", True, pubsub=WampServerProtocol.SUBSCRIBE)
        #reactor.callLater(5, self.sendEvent)

    #def sendEvent(self, event):
    #    self.dispatch("http://example.com/simple", event)


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    # websocket stuff
    debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
    factory = WampServerFactory("ws://0.0.0.0:9000", debugWamp = debug)
    factory.protocol = PubSubServer
    factory.setProtocolOptions(allowHixie76 = True)
    listenWS(factory)

    # rabbitmq stuff
    parameters = pika.ConnectionParameters()
    cc = protocol.ClientCreator(reactor, twisted_connection.TwistedProtocolConnection, parameters)
    d = cc.connectTCP('localhost', 5672)
    d.addCallback(lambda protocol: protocol.ready)
    pika_consumer = PikaConsumer(factory)
    d.addCallback(pika_consumer.run)

    reactor.run()
