import math
 
from twisted.internet import reactor
 
from autobahn.websocket import listenWS
from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampServerProtocol
 
 
class Calc:
 
   @exportRpc
   def add(self, x, y):
      return x + y
 
   @exportRpc
   def sub(self, x, y):
      return x - y
 
   @exportRpc
   def square(self, x):
      MAX = 1000
      if x > MAX:
         raise Exception("http://example.com/error#number_too_big",
                         "%d too big for me, max is %d" % (x, MAX),
                         MAX)
      return x * x
 
   @exportRpc
   def sum(self, list):
      return reduce(lambda x, y: x + y, list)
 
   @exportRpc
   def pickySum(self, list):
      errs = []
      for i in list:
         if i % 3 == 0:
            errs.append(i)
      if len(errs) > 0:
         raise Exception("http://example.com/error#invalid_numbers",
                         "one or more numbers are multiples of 3",
                         errs)
      return reduce(lambda x, y: x + y, list)
 
   @exportRpc
   def sqrt(self, x):
      return math.sqrt(x)
 
   @exportRpc("asum")
   def asyncSum(self, list):
      d = defer.Deferred()
      reactor.callLater(3, d.callback, self.sum(list))
      return d
 
 
class SimpleServerProtocol(WampServerProtocol):
 
   def onSessionOpen(self):
      self.calc = Calc()
      self.registerForRpc(self.calc, "http://example.com/simple/calc#")
 
 
if __name__ == '__main__':
 
   factory = WampServerFactory("ws://mozart.kawigi.com:9000", debugWamp = True)
   factory.protocol = SimpleServerProtocol
   listenWS(factory)
 
   reactor.run()
