import math

class NetworkDijkstra:

   def __init__(self, source_id, network_map):
      self._source_id = source_id
      self._network_map = network_map
      self._cost = None
      self._pred = None


   @property
   def source_id(self):
      return self._source_id


   @property
   def network_map(self):
      return self._network_map


   @network_map.setter
   def network_map(self, network_map):
      self._network_map = network_map


   @property
   def cost(self):
      return self._cost


   @cost.setter
   def cost(self, cost):
      self._cost = cost


   @property
   def pred(self):
      return self._pred


   @pred.setter
   def pred(self, pred):
      self._pred = pred


   # Get minimum cost node id from unvisited set
   def minCost(self, unvisited, cost):
      minCost = math.inf
      minCostNode = None

      for v in unvisited:
         if cost[v] < minCost:
            minCost = cost[v]
            minCostNode = v

      return minCostNode


   # Run Dijkstra's algorithm on network map and store cost and pred
   def run_dijkstra(self):
      # cost = dist, pred = prev, unvisted = Q 
      # common alternatives in pseudo code
      cost = {}
      pred = {}
      unvisited = set()
      unvisited.add(self.source_id)

      # Set cost for routers to inf and pred to None then add ids to unvisited
      for key, val in self.network_map.items():
         cost[key] = math.inf
         pred[key] = None
         unvisited.add(key)

      # Cost for source is 0
      cost[self.source_id] = 0

      # Loop while there are still unvisited routers.
      while unvisited:
         # Set v to lowest cost router in unvisited, 
         # at the start that is always the source.
         if self.source_id in unvisited:
            v = self.source_id
         else:
            v = self.minCost(unvisited, cost)

         # The router v is now visited remove it from unvisited.
         unvisited.remove(v)

         # Compare cost v-->u to cost[u] and choose the one that's lower
         for u, val in self.network_map[v].items():
            # Add the weight of the edge from v to u to the cost of v for path cost
            alt = cost[v] + val['weight']
            alt = round(alt, 1)

            # If new path is less that previous cost to get to u 
            # change cost[u] and add to pred
            if alt < cost[u]:
               cost[u] = alt
               pred[u] = { 'id' : v, 'address' : val['address'] }

      # set cost and pred fields
      self.cost = cost
      self.pred = pred


   # Traverse through pred to get the lowest cost path for dest
   def getPath(self, dest):
      v = dest
      path = v

      while self.pred[v] is not None:
         path = self.pred[v]['id'] + path
         v = self.pred[v]['id']

      return path


   # Print lowest cost paths for source router
   def print_dijkstra(self):
      print("I am Router {0}".format(self.source_id))

      for key, val in self.cost.items():
         if key != self.source_id:
            path = self.getPath(key)
            print("Least cost path to router {0}: {1} and the cost is {2}".format(key, path, val))
