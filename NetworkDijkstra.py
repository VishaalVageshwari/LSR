class NetworkDijkstra:

   def __init__(self, source_id, network_map):
      self._source_id = source_id
      self._network_map = network_map


   @property
   def source_id(self):
      return self._source_id


   @property
   def network_map(self):
      return self._network_map


   @network_map.setter
   def network_map(self, network_map):
      self._network_map = network_map

   
   def run_dijkstra:
      print("Run Dijkstra!")