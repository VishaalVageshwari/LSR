import sys, re
from socket import *
from threading import *
from time import time, sleep
from ConfigParser import ConfigParser
from NetworkDijkstra import NetworkDijkstra

# Tested using Python 3.7.3

HOST = '127.0.0.1'
UPDATE_INTERVAL = 1
ROUTER_UPDATE_INTERVAL = 30
MAX_HEARTBEATS = 3
LAST_LSA_CUSHION = 0.01

class Router:

   def __init__(self, id, address, count, neighbours):
      self._id = id
      self._address = address
      self._count = count
      self._neighbours = neighbours
      self._seq = 0
      self._received_seq = {}
      self._lsa = self.create_lsa()
      self._socket = self.create_socket()
      self._network_map = self.init_network_map()
      self._network_dijkstra = NetworkDijkstra(self.id, self.network_map)


   @property
   def id(self):
      return self._id


   @property
   def count(self):
      return self._count


   @property
   def neighbours(self):
      return self._neighbours


   @property
   def address(self):
      return self._address


   @property
   def socket(self):
      return self._socket


   @property
   def seq(self):
      return self._seq


   @seq.setter
   def seq(self, seq):
      self._seq = seq


   @property
   def received_seq(self):
      return self._received_seq


   @property
   def lsa(self):
      return self._lsa


   @lsa.setter
   def lsa(self, lsa):
      self._lsa = lsa


   @property
   def network_map(self):
      return self._network_map


   @property
   def network_dijkstra(self):
      return self._network_dijkstra


   # Create a UDP socket for the router using its address.
   def create_socket(self):
      router_socket = socket(AF_INET, SOCK_DGRAM)
      router_socket.bind(self.address)
      return router_socket


   # Intialize network map for the router.
   def init_network_map(self):
      network_map = {}
      network_map[self.id] = {}

      # Add this routers neighbours to network map.
      for key, val in self.neighbours.items():
         network_map[self.id][key] = { 'address' : val['address'], 'weight' : val['weight'] }

      return network_map


   # Create Link State Advertisement(LSA) to broadcast.
   def create_lsa(self):
      # Add header containing LSA sequence number, router id,
      # host, port and neighbour count.
      message = (
               str(self.seq) + ' ' +
               self.id + ' ' +
               self.address[0] + ' ' +
               str(self.address[1]) + ' ' +
               str(self.count) + '\n'
      )

      # Add details of neighbours to LSA including neighbour id e.g. AB,
      # neigbour host, neighbour port, weight to neighbour router.
      for key, val in self.neighbours.items():
         host = val['address'][0]
         port = str(val['address'][1])
         edge_weight = str(val['weight'])

         # If the last lsa was not received within (MAX_HEARTBEATS * UPDATE_INTERVAL) + LAST_LSA_CUSHION 
         # seconds it would mean MAX_HEARTBEAT(3) missed LSAs from a neighbour. 
         # That neighbour is considered dead until its neighbours receives another LSA from it.
         if (time() - val['last_received']) > ((MAX_HEARTBEATS * UPDATE_INTERVAL) + LAST_LSA_CUSHION):
            alive_status = 'dead'
         else:
            alive_status = 'alive'

         message = (
                  message + 
                  key + ' ' + 
                  host + ' ' +
                  port + ' ' +
                  edge_weight + ' ' +
                  alive_status + '\n'
         )

      return message


   # Parse and store details of the LSA if relevant.
   # Return a tuple with the id of the router that sent the and
   # True if the router should foward the LSA and False otherwise.
   def store_lsa_info(self, lsa):
      lines = re.split('\n', lsa)

      # Extract header info from LSA.
      header = lines.pop(0)
      header_info = header.split()
      lsa_seq = int(header_info.pop(0))
      orgin_id = header_info.pop(0)
      orgin_addr = (header_info.pop(0), int(header_info.pop(0)))
      neighbour_count = int(header_info.pop(0))

      # If the orgin of the lsa was a neigbour record the current time as last received.
      if orgin_id in self.neighbours:
         self.neighbours[orgin_id]['last_received'] = time()

      # Store sequence number if it is higher than the previous otherwise
      # return Flase in foward status, there is no need to foward this LSA.
      if orgin_id not in self.received_seq or lsa_seq > self.received_seq[orgin_id]:
         self.received_seq[orgin_id] = lsa_seq
         self.network_map[orgin_id] = {}
      elif lsa_seq > self.received_seq[orgin_id]:
         self.received_seq[orgin_id] = lsa_seq
      else:
         return (orgin_id, False)

      # Extract and store neigbour info in network map.
      for i in range(0, neighbour_count):
         edge = lines[i]
         neighbour_info = edge.split()
         neighbour_id = neighbour_info.pop(0)
         neighbour_addr = (neighbour_info.pop(0), int(neighbour_info.pop(0)))
         edge_weight = float(neighbour_info.pop(0))
         alive_status = neighbour_info.pop(0)

         # If the neighbour is alive store its info otherwise remove every instance of it from network map
         # and received sequence numbers.
         if alive_status == "alive":
            if neighbour_id not in self.network_map[orgin_id]:
               self.network_map[orgin_id][neighbour_id] = { 'address' : neighbour_addr, 'weight' : edge_weight }
            else:
               self.network_map[orgin_id][neighbour_id]['address'] = neighbour_addr
               self.network_map[orgin_id][neighbour_id]['weight'] = edge_weight
         else:
            self.remove_dead_router(neighbour_id)

      return (orgin_id, True)


   # If a dead router is anywhere in the network map or 
   # received sequence number dictionaries remove it.
   def remove_dead_router(self, id):
      # Remove the router's entry in the network map
      if id in self.network_map:
         del self.network_map[id]

      # Remove the router's entry as neighbours to other routers in the network map
      for key, val in self.network_map.items():
         if id in val:
            del val[id]

      # Remove received sequence entry for for this router
      if id in self.received_seq:
         del self.received_seq[id]


   # Foward the LSA to relevant neighbours.
   def forward(self, lsa, orgin_id, sender_addr):
      # Foward LSA to neighbours
      for key, val in self.neighbours.items():
         neigbour_id = key
         neighbour_addr = val['address']

         # If the neigbour is not the sender or the orginal router send LSA
         if neighbour_addr != sender_addr and neigbour_id != orgin_id:
            self.socket.sendto(lsa.encode(), neighbour_addr)


   # Broadcast LSA to neighbours every UPDATE_INTERVAL (1 sec).
   def broadcast(self):
      while True:
         if self.seq != 0:
            self.lsa = self.create_lsa()

         # send LSA to neighbours
         for key, val in self.neighbours.items():
            self.socket.sendto(self.lsa.encode(), val['address'])

         self.seq = self.seq + 1
         sleep(UPDATE_INTERVAL)           


   # Receive LSAs from socket, process and foward them.
   def receive(self):
      while True:
         # Receive LSA and sender address from socket
         lsa, sender_addr = self.socket.recvfrom(1024)
         lsa = lsa.decode()
         orgin_id, forward_status = self.store_lsa_info(lsa)
         
         # If foward status was True foward LSA
         if forward_status == True:
            self.forward(lsa, orgin_id, sender_addr)
         
      self.socket.close()


   # Run Dijkstra's algorithm on a copy of the network map every ROUTER_UPDATE_INTERVAL (30 secs)
   # and print out the appropriate results
   def run_network_dijkstra(self):
      while True:
         sleep(ROUTER_UPDATE_INTERVAL)
         self.network_dijkstra.network_map = self.network_map.copy()
         self.network_dijkstra.run_dijkstra()
         self.network_dijkstra.print_dijkstra()

   
   # Function to start threads for link state routing, one thread for broadcasting,
   # one thread for receiving link state advertisements and the set the main thread for dijkstra's.
   def run_LSR(self):
      broadcast_thread = Thread(target=self.broadcast)
      broadcast_thread.daemon = True
      receiver_thread = Thread(target=self.receive)
      receiver_thread.daemon = True
      broadcast_thread.start()
      receiver_thread.start()
      self.run_network_dijkstra()


if __name__ == "__main__":
   # Check command line arguments
   if (len(sys.argv) != 2):
      print("Usage: Lsr.py <filename>")

   # Extract info from config file and create corresponding router
   cp = ConfigParser(sys.argv[1])
   ri = cp.get_router_info(HOST)
   router = Router(ri[0], ri[1], ri[2], ri[3])

   # Run Link State Routing threads
   router.run_LSR()