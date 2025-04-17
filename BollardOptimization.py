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
            edge["car_speed"]       = self.car_speed
            edge["bike_speed"]      = self.bike_speed
            edge["car_time"]        = edge["length"]/self.car_speed
            edge["bike_time"]       = edge["length"]/self.bike_speed

        self.plot_graph_simple(igraph)
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
            bbox=(1000, 1000),
            margin=50
        )
        print(f"Graph saved to {filename}")


    def calculatePathCost(self, graph, path):
        cost = 0
        for edge in path:
            cost += graph.es[edge]["car_time"]
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
    

    def searchOptimization(self, source, destination, max_bollards):
        print("Original Path (before any bollards):")
        for edge_index in range(len(self.graph.es)):
            edge = self.graph.es[edge_index]
            edge_car_time = edge["car_time"]
            print(f"Edge Index: {edge_index}, Car Time: {edge_car_time}")

        original_path = self.graph.get_shortest_paths(source, to = destination, weights = "car_time", output = "epath")[0]
        print("Original Shortest Path (Edge Indices):")
        for edge_index in original_path:
            edge = self.graph.es[edge_index]
            edge_car_time = edge["car_time"]
            print(f"Edge Index: {edge_index}, Car Time: {round(edge_car_time, 2)}s")

        original_graph_cost = self.calculatePathCost(self.graph, original_path)

        best_dilation           = float("inf")
        best_edges_to_slow      = None
        best_modified_path           = None
        edge_indices            = range(len(self.graph.es))
        for num_of_bollards in range(1, max_bollards + 1):
            combinations = itertools.combinations(edge_indices, num_of_bollards)
            for combination in combinations:
                    trial_dilation, modified_path = self.dilation(source, destination, combination, original_graph_cost)
                    #print(combination, trial_dilation, modified_path)
                    if trial_dilation < best_dilation:
                        best_modified_path  = modified_path
                        best_dilation       = trial_dilation
                        best_edges_to_slow  = combination

        print("Best Modified Path:", best_modified_path)
        print("Best Maximum Dilation (Greedy):", best_dilation)
        print("Bollards placed on edges:", best_edges_to_slow)
        return best_dilation, best_edges_to_slow