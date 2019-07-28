import math

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

   def minCost(self, unvisited, cost):
      minCost = math.inf
      minCostNode = None

      for v in unvisited:
         if cost[v] < minCost:
            minCost = cost[v]
            minCostNode = v

      return minCostNode

   def run_dijkstra(self):
      print("Run Dijkstra!")
      print(self.network_map)

      cost = {}
      pred = {}
      unvisited = set()

      for key, val in self.network_map.items():
         cost[key] = math.inf
         pred[key] = None
         unvisited.add(key)

      cost[self.source_id] = 0

      while unvisited:
         if self.source_id in unvisited:
            v = self.source_id
         else:
            v = self.minCost(unvisited, cost)

         unvisited.remove(v)

         for u, val in self.network_map[v].items():
            alt = cost[v] + val['weight']

            if alt < cost[u]:
               cost[u] = alt
               pred[u] = { 'id': v, 'address' : val['address'] }

      print(cost)
      print(pred)
