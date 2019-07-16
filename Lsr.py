import sys
from socket import *
from threading import *
from time import time, sleep
from ConfigParser import ConfigParser

HOST = '127.0.01'
UPDATE_INTERVAL = 1
ROUTER_UPDATE_INTERVAL = 30

class LSAParser:

   def __init__(self)

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
      self._lsa_parser = LSAParser() 
      self._network_map = self.init_network_map()

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

   def create_socket(self):
      router_socket = socket(AF_INET, SOCK_DGRAM)
      router_socket.bind(self.address)
      return router_socket

   def create_lsa(self):
      message = (
               str(self.seq) + ' ' +
               self.id + ' ' +
               self.address[0] + ' ' +
               self.address[1] + '\n'
      )

      print(self.neighbours)

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

   def init_network_map(self):
      network_map = {}

      for key, val in self.neighbours.items():
         edge_id = self.id + key
         network_map[edge_id] = { 'address' : val['address'], 'weight' : val['weight'] }

      print(network_map)
      return network_map

   def broadcast(self):
      while True:
         if self.seq != 0:
            self.lsa = self.create_lsa()

         for key, val in self.neighbours.items():
            self.socket.sendto(self.ls_packet, val['address'])

         self.seq += 1
         sleep(UPDATE_INTERVAL)

   def receive(self):
      while True:
         ls_packet, sender_addr = self.socket.recvfrom(1024)

if __name__ == "__main__":
   if (len(sys.argv) != 2):
      print("Usage: Lsr.py <filename>")

   cp = ConfigParser(sys.argv[1])
   ri = cp.get_router_info(HOST)
   router = Router(ri[0], ri[1], ri[2], ri[3])