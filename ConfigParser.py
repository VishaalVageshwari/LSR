from time import time

class ConfigParser:

   def __init__(self, filename):
      self._filename = filename
      self._config = self.read_config()


   @property
   def filename(self):
      return self._filename


   @property
   def config(self):
      return self._config


   # Open and read contents of config file
   def read_config(self):
      config_file = open(self.filename, 'r')
      config = config_file.read()
      config_file.close()
      return config


   # Get router info from info in config file
   def get_router_info(self, host):
      info = self.config.split()
      router_id = info.pop(0)
      router_port = int(info.pop(0))
      neighbour_count = int(info.pop(0))

      neighbours = {}

      # Fill with neigbour dictonary with neighbour info
      for i in range(0, neighbour_count):
         neighbour_id = info.pop(0)
         edge_weight = float(info.pop(0))
         neighbour_port = int(info.pop(0))
         neighbours[neighbour_id] = { 'address' : (host, neighbour_port), 'weight' : edge_weight, 'last_received' : time() }

      return (router_id, (host, router_port), neighbour_count, neighbours)