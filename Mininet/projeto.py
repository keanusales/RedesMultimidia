from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

def network(number_servers: int, number_gamers: int):
  net = Mininet()
  servers = [net.addHost(f'server{i}') for i in range(number_servers)]
  controllers = [net.addController(f'cont{i}') for i in range(number_servers)]
  for server, controller in zip(servers, controllers): net.addLink(server, controller)
  main_controller = net.addController('contMain')
  for controller in controllers: net.addLink(main_controller, controller)
  gamers = [net.addHost(f'gamer{i}') for i in range(number_gamers)]
  for gamer in gamers: net.addLink(main_controller, gamer)
  return net

def test_network(net: Mininet):
  net.start()
  print( "Dumping host connections" )
  dumpNodeConnections(net.hosts)
  print( "Testing network connectivity" )
  net.pingAll()
  net.stop()

if __name__ == '__main__':
  setLogLevel('info')
  test_network(network(10, 50))