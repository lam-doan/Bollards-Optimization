from igraph import Graph
import random
import itertools

"""
graph.es: return lists of edges in the graph
each edge will be assigned random weights (velocity in this scenario)
to retrieve their velocity: graph.es[edge][]
"""

class BollardOptimization:
    def __init__(self, rows, cols, car_speed, bike_speed):
        self.rows = rows
        self.cols = cols
        self.car_speed = car_speed
        self.bike_speed = bike_speed
        self.graph = self.createGraph()

    def createGraph(self):
        # create a graph with rows*cols vertices
        graph = Graph(n = self.rows * self.cols)
        for row in range(self.rows):
            for col in range(self.cols):
                current = row * self.cols + col
                # Connect to the right neighbor if it exists
                if col < self.cols - 1:
                    graph.add_edge(current, current + 1)
                # Connect to the bottom neighbor if it exists
                if row < self.rows - 1:
                    graph.add_edge(current, current + self.cols)
        layout = graph.layout("grid")
        # plot(graph, layout=layout, target='grid_graph.png')
        self.list_of_vehicles = []
        for edge in graph.es:
            vehicle_type = random.choice(["car", "bike"])
            if vehicle_type == "car":
                edge["speed"] = 40
                edge["travel_time"] = 0.125
            elif vehicle_type == "bike":
                edge["speed"] = 20
                edge["travel_time"] = 0.25
            self.list_of_vehicles.append(vehicle_type)

        print(graph.es["travel_time"])
        print(self.list_of_vehicles)

        return graph


    def getModifiedGraph(self, edge_settings):
        """
        Create a modified graph based on edge settings
        edge_settings: A list indicating the speed setting for each edge ('car' or 'bike').
        """
        modified_graph = self.graph.copy()
        for i in range(len(self.graph.es)):
            if edge_settings[i] == "car":
                modified_graph.es[i]["speed"] = self.car_speed
            else:
                modified_graph.es[i]["speed"] = self.bike_speed

        return modified_graph

    def dilation(self, modified_graph, source, destination):
        """
        Calculate dilation using the original and modified graphs.
        Calculate the sum of time needed for both graphs (time = path length/speed)
        Dilation = time(modified)/time(original)
        """
        # return a list of edges that sum of time travel is lowest
        original_path = self.graph.get_shortest_path(source, to = destination, weights = self.graph.es["travel_time"], output = "epath")
        original_graph_cost = 0
        for edge in original_path:
            original_graph_cost += (self.graph.es[edge]["travel_time"])

        modified_path = modified_graph.get_shortest_path(source, to = destination,  weights = modified_graph.es["travel_time"], output = "epath")
        modified_graph_cost = 0 
        for edge in modified_path:
            modified_graph_cost += (modified_graph.es[edge]["travel_time"])

        return modified_graph_cost/original_graph_cost
    
    def bruteForce(self, source, destination):
        """
        This function tries all possibilities of setting and find the one that has lowest dilation
        """
        optimized_dilation = float('inf') # set to a random max float number
        optimized_setting = []
        
        #Create a list of list of random settings from each edge
        #Each edge will randomly be assigned as either 'car' or 'bike'
        list_of_settings = itertools.product(["car", "bike"], repeat = len(self.graph.es))

        for setting in list_of_settings:
            if setting == self.list_of_vehicles: continue
            else:
                modified_graph = self.getModifiedGraph(setting)
                dilation = self.dilation(modified_graph, source, destination)
                if dilation < optimized_dilation:
                    optimized_dilation = dilation
                    optimized_setting = setting

        print(optimized_dilation)
        print(optimized_setting)
        return optimized_dilation, optimized_setting