import sys
 
from twisted.python import log
from twisted.internet import reactor, defer
from twisted.web.server import Site
from twisted.web.static import File
 
from autobahn.websocket import listenWS
from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampServerProtocol
 
 
class RpcServer1Protocol(WampServerProtocol):
   """
   A minimalistic RPC server.
   """
 
   def onSessionOpen(self):
      # When the WAMP session has been established, register any methods
      # remoted on this class for RPC
      self.registerForRpc(self, "http://example.com/simple/calc#")
 
   @exportRpc("add")
   def add(self, x, y):
      """
      A simple remoted method which can be called via RPC from any WAMP client.
      """
      return x + y
 
 
if __name__ == '__main__':
 
   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False
 
   factory = WampServerFactory("ws://0.0.0.0:9000", debugWamp = debug)
   factory.protocol = RpcServer1Protocol
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)
 
   reactor.run()
