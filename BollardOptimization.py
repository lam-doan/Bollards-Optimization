from igraph import Graph
import osmnx as ox
import networkx as nx
import random
import itertools

"""
graph.es: return lists of edges in the graph
each edge will be assigned random weights (velocity in this scenario)
to retrieve their velocity: graph.es[edge][]
"""

class BollardOptimization:
    def __init__(self, car_speed, bike_speed):
        self.car_speed = car_speed
        self.bike_speed = bike_speed
        self.list_of_vehicles = []
        self.graph = self.osmtoIgraph()

    def retrieveFromOSM(self):
        graph_networkx_bike = ox.graph.graph_from_bbox((-117.935413, 33.881272, -117.932688, 33.879985), network_type= "bike")
        graph_networkx_car = ox.graph.graph_from_bbox((-117.935413, 33.881272, -117.932688, 33.879985), network_type= "drive")
        graph_networkx = nx.compose(graph_networkx_bike, graph_networkx_car)
        return graph_networkx
    
    def osmtoIgraph(self):
        graph_networkx = self.retrieveFromOSM()
        igraph         = Graph.from_networkx(graph_networkx)
        
        for index, nodeID in enumerate(graph_networkx.nodes()):
            igraph.vs[index]["osm_ID"] = nodeID
        
        for edge in igraph.es:
            vehicle_type = random.choice(["car", "bike"])
            if vehicle_type == "car":
                edge["speed"]       = self.car_speed
                edge["car_time"]    = edge['length'] / self.car_speed
                edge["bike_time"]   = edge['length'] / self.bike_speed
            elif vehicle_type == "bike":
                edge["speed"]       = self.bike_speed
                edge["car_time"]    = edge['length'] / self.bike_speed
                edge["bike_time"]   = edge['length'] / self.bike_speed
            self.list_of_vehicles.append(vehicle_type)
        
        return igraph

    def getModifiedGraph(self, edge_settings):
        """
        Create a modified graph based on edge settings
        edge_settings: A list indicating the speed setting for each edge ('car' or 'bike').
        """
        modified_graph = self.graph.copy()

        for i in range(len(self.graph.es)):
            modified_graph.es[i]["speed"] *= random.uniform(0.9, 1.1)  # Adjust the car speed by ±10%
            if edge_settings[i] == "car":
                # Recalculate car travel time based on the new speed
                modified_graph.es[i]["car_time"] = 1 / modified_graph.es[i]["speed"]
            else:
                # Recalculate car travel time based on the new speed
                modified_graph.es[i]["car_time"] = 1 / modified_graph.es[i]["speed"]
        return modified_graph
    
    def calculatePathCost(self, graph, path, weight_key):
        """
        Calculate the total cost (time) of a path based on the weight key.
        """
        cost = 0
        for edge in path:
            cost += graph.es[edge][weight_key]
        return cost
    

    def dilation(self, modified_graph, source, destination, mode):
        """
        Calculate dilation using the original and modified graphs for a given mode

        Calculate the sum of time needed for both graphs (time = path length/speed)
        Dilation = time(modified)/time(original)
        """

        if mode == "car":
            weight_key  = "car_time"
        else:
            weight_key  = "bike_time"

        # return a list of edges that sum of time travel is lowest

        original_path = self.graph.get_shortest_paths(source, to = destination, weights = weight_key, output = "epath")[0]
        original_graph_cost = self.calculatePathCost(self.graph, original_path, weight_key)

        modified_path = modified_graph.get_shortest_paths(source, to = destination, weights = weight_key, output="epath")[0]
        modified_cost = self.calculatePathCost(modified_graph, modified_path, weight_key)
        dilation = modified_cost/original_graph_cost

        return dilation
    

    def bruteForce(self, source, destination):
        edge_count = len(self.graph.es)
        best_max_dilation = float('inf')
        best_setting = None

        for edge_settings in itertools.product(["car", "bike"], repeat=edge_count):
            modified_graph = self.getModifiedGraph(edge_settings)
            
            car_dilation = self.dilation(modified_graph, source, destination, "car")
            bike_dilation = self.dilation(modified_graph, source, destination, "bike")
            
            max_dilation = max(car_dilation, bike_dilation)
            if max_dilation < best_max_dilation:
                best_max_dilation = max_dilation
                best_setting = edge_settings

        print("Best Maximum Dilation:", best_max_dilation)
        print("Best Edge Settings:", best_setting)
        return best_max_dilation, best_setting