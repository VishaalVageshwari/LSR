import sys, re
from socket import *
from threading import *
from time import time, sleep
from ConfigParser import ConfigParser

HOST = '127.0.01'
UPDATE_INTERVAL = 1
ROUTER_UPDATE_INTERVAL = 30

class Router:

   def __init__(self, id, address, count, neighbours):
      self._id = id
      self._address = address
      self._count = count
      self._neighbours = neighbours
      self._socket = self.create_socket
      self._seq = 0
      self._lsa = self.create_lsa()
      self._received_seq = {}
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


   @property
   def lsa(self):
      return self._lsa


   @property
   def received_seq(self):
      return self._received_seq


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


   # Create Link State Advertisement(LSA) to broadcast.
   def create_lsa(self):
      # Add header containing LSA sequence number, router id,
      # host, port and neigbour count .
      message = (
               str(self.seq) + ' ' +
               self.id + ' ' +
               self.address[0] + ' ' +
               self.address[1] + ' ' +
               self.count + '\n'
      )

      print(self.neighbours)

      # Add details of neigbours to LSA including edge_id e.g. AB,
      # neigbour host, neigbour port, weight to neigbour router.
      for key, val in self.neighbours.items():
         edge_id = self.id + key
         host = val['address'][0]
         port = val['address'][1]
         edge_weight = str(val['weight'])
         message = (
                  message + 
                  edge_id + ' ' + 
                  host + ' ' +
                  port + ' ' +
                  edge_weight + '\n'
         )

      print(message, end='')

      return message


   # Parse and store details of the LSA if relevant.
   # Return a tuple with the id of the router that sent the and
   # True if the router should foward the LSA and False otherwise.
   def store_lsa_info(self, lsa):
      lines = re.split('\n', lsa)

      # Extract header info from LSA.
      header = lines.pop(0)
      header_info = header.split()
      lsa_seq = header_info.pop(0)
      orgin_id = header_info.pop(0)
      orgin_addr = (header_info.pop(0), header_info.pop(0))
      neighbour_count = header_info.pop(0)

      # Store sequence number if it is higher than the previous otherwise
      # return Flase in foward status, there is no need to foward this LSA.
      if orgin_id not in self.received_seq or lsa_seq > self.received_seq[orgin_id]:
         self.received_seq[orgin_id] = lsa_seq
      else:
         return (orgin_id, False)

      # Extract and store neigbour info in network map.
      for i in range(0, neighbour_count):
         edge = lines[i]
         neigbour_info = edge.split()
         edge_id = neighbour_info.pop(0)
         neighbour_address = (neigbour_info.pop(0), neigbour_info.pop(0))
         edge_weight = neigbour_info.pop(0)
         
         if edge_id not in network_map:
            network_map[edge_id] = { 'orgin_address' : orgin_id, 'n_address' : neighbour_address, 'weight' : edge_weight }
         else:
            network_map[edge_id]['n_address'] = neighbour_address
            network_map[edge_id]['weight'] = edge_weight

      return (orgin_id, True)
       

   # Intialize network map for the router.
   def init_network_map(self):
      network_map = {}

      # Add this routers neighbours to network map.
      for key, val in self.neighbours.items():
         edge_id = self.id + key
         network_map[edge_id] = { 'o_address' : self.address, 'n_address' : val['address'], 'weight' : val['weight'] }

      print(network_map)
      return network_map


   # Foward the LSA to relevant neighbours.
   def forward(self, lsa, orgin_id):
      # Foward LSA to neighbours
      for key, val in self.neighbours.items():
         neigbour_id = key
         neighbour_addr = val['address']

         # If the neigbour is not the sender or the orginal router send LSA
         if neighbour_addr != sender and neigbour_id != orgin_id:
            self.socket.sendto(lsa, neighbour_addr)


   # Broadcast LSA to neighbours every UPDATE_INTERVAL (1 sec).
   def broadcast(self):
      while True:
         if self.seq != 0:
            self.lsa = self.create_lsa()

         # send LSA to neighbours
         for key, val in self.neighbours.items():
            self.socket.sendto(self.lsa, val['address'])

         self.seq += 1
         sleep(UPDATE_INTERVAL)            


   # Receive LSAs from socket, process and foward them.
   def receive(self):
      while True:
         # Receive LSA and sender address from socket
         lsa, sender_addr = self.socket.recvfrom(1024)
         orgin_id, forward_status = self.store_lsa_info(lsa)
         
         # If foward status was True foward LSA
         if forward_status == True:
            self.forward(lsa, orgin_id, sender_addr)

   def run_network_dijkstra(self):
      while True:
         sleep(ROUTER_UPDATE_INTERVAL)
         self.network_dijkstra.network_map = self.network_map
         self.network_dijkstra.run_dijkstra()



if __name__ == "__main__":
   # Check command line arguments
   if (len(sys.argv) != 2):
      print("Usage: Lsr.py <filename>")

   # Extract info from config file and create corresponding router
   cp = ConfigParser(sys.argv[1])
   ri = cp.get_router_info(HOST)
   router = Router(ri[0], ri[1], ri[2], ri[3])