from igraph import plot
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
        self.graph = self.osmtoIgraph()

    def retrieveFromOSM(self):
        graph_networkx_bike = ox.graph.graph_from_bbox((-117.938093, 33.883393, -117.928533, 33.877035), network_type= "bike")
        graph_networkx_car = ox.graph.graph_from_bbox((-117.938093, 33.883393, -117.928533, 33.877035), network_type= "drive")
        graph_networkx = nx.compose(graph_networkx_bike, graph_networkx_car)
        return graph_networkx
    
    def osmtoIgraph(self):
        graph_networkx = self.retrieveFromOSM()
        igraph         = Graph.from_networkx(graph_networkx)
        
        for index, nodeID in enumerate(graph_networkx.nodes()):
            igraph.vs[index]["osm_ID"] = nodeID
        
        for edge in igraph.es:
            edge["car_speed"]       = self.car_speed
            edge["bike_speed"]      = self.bike_speed
            edge["car_time"]        = edge["length"]/self.car_speed
            edge["bike_time"]       = edge["length"]/self.bike_speed

        self.plot_graph_simple(igraph)
        print("Number of vertices", len(igraph.vs))
        return igraph

    def plot_graph_simple(self, graph, filename="graph.png"):
        for edge in graph.es:
            edge["label"] = f"{edge.index}, {round(edge['car_time'], 2)}s"

        layout = graph.layout("grid")

        plot(
            graph,
            layout=layout,
            target=filename,
            vertex_label=graph.vs["osm_ID"],
            edge_label=graph.es["label"],
            vertex_size=10,
            edge_arrow_size=0.5,
            bbox=(600, 600),
            margin=50
        )
        print(f"Graph saved to {filename}")


    def calculatePathCost(self, graph, path):
        cost = sum(graph.es[edge]["car_time"] for edge in path)
        return cost  

    def dilation(self, source, destination, slowed_edges, original_graph_cost):
        modified_graph = self.graph.copy()
        for i in range(len(modified_graph.es)):
            if i in slowed_edges:
                modified_graph.es[i]["car_speed"] = self.bike_speed
                modified_graph.es[i]["car_time"]  = self.graph.es[i]["bike_time"]

        modified_path = modified_graph.get_shortest_paths(source, to = destination, weights = "car_time", output="epath")[0]
        modified_cost = self.calculatePathCost(modified_graph, modified_path)
        dilation = modified_cost/original_graph_cost

        return dilation, modified_path
    
    def searchOptimization(self, source, destination):    
        """
        print("Original Path (before any bollards):")
        for edge_index in range(len(self.graph.es)):
            edge = self.graph.es[edge_index]
            edge_car_time = edge["car_time"]
            print(f"Edge Index: {edge_index}, Car Time: {round(edge_car_time, 2)}s")
        """
        
        # find the shortest path for bike
        best_car_path_before_bollards = self.graph.get_shortest_paths(source, to = destination, weights = "car_time", output = "epath")[0]
        best_car_cost_before_bollards = self.calculatePathCost(self.graph, best_car_path_before_bollards)

        # find the shortest path for cyclist (A)
        bike_shortest_path = self.graph.get_shortest_paths(source, to = destination, weights = "bike_time", output="epath")[0]
        bike_shortest_path_time = sum(self.graph.es[edge]["bike_time"] for edge in bike_shortest_path)

        best_dilation                     = float("inf")
        edges_put_bollards                = None
        best_car_path_after_bollards      = None
        list_of_index_of_edges            = range(len(self.graph.es))
        all_possible_paths = []

        number_of_bollards = len(bike_shortest_path)
        combinations = itertools.combinations(list_of_index_of_edges, number_of_bollards)
        # make sure bike_shortest_path is subset of possible combination
        for combination in combinations:
            if (set(bike_shortest_path)).issubset(set(combination)):
                all_possible_paths.append(combination)
        
        for path in all_possible_paths:
            curr_dilation, modified_path = self.dilation(source, destination, path, best_car_cost_before_bollards)
            if curr_dilation < best_dilation:
                best_car_path_after_bollards  = modified_path
                best_dilation                 = curr_dilation
                edges_put_bollards            = path

        print("Best Path for Bike:", bike_shortest_path)
        print("Best Time Path for Bike:", round(bike_shortest_path_time, 2), "s")
        print()
        print("[Before Bollards] Best Path for Car:", best_car_path_before_bollards)
        print("[Before Bollards] Best Time Path for Car:", round(best_car_cost_before_bollards, 2), "s")
        print("Bollards placed on edges:", edges_put_bollards)
        print("[After Bollards] Best Path for Car:", best_car_path_after_bollards)
        print("Best Minimum Dilation:", best_dilation)

        return edges_put_bollards, best_car_path_after_bollards, best_dilation