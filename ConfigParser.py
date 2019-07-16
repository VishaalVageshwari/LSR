class ConfigParser:

   def __init__(self, filename):
      self._filename = filename
      self._config = self.read_config()

   @property
   def filename(self):
      return self._filename

   @filename.setter
   def filename(self, filename):
      self._filename = filename

   @property
   def config(self):
      return self._config

   @config.setter
   def config(self, config):
      self._config = config

   def read_config(self):
      config_file = open(self.filename, 'r')
      config = config_file.read()
      config_file.close()
      return config

   def get_router_info(self, host):
      info = self.config.split()
      router_id = info.pop(0)
      router_port = info.pop(0)
      neighbour_count = int(info.pop(0))

      neighbours = {}

      for i in range(0, neighbour_count):
         neighbour_id = info.pop(0)
         edge_weight = float(info.pop(0))
         neighbour_port = info.pop(0)
         neighbours[neighbour_id] = { 'address' : (host, neighbour_port), 'weight' : edge_weight }

      return (router_id, (host, router_port), neighbour_count, neighbours)