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

        print(self.list_of_vehicles)

        return graph


    def getModifiedGraph(self, edge_settings): # need another graph for bike 
        """
        Create a modified graph based on edge settings
        edge_settings: A list indicating the speed setting for each edge ('car' or 'bike').
        """
        modified_graph = self.graph.copy()

        for i in range(len(self.graph.es)):
            if edge_settings[i] == "car":
                modified_graph.es[i]["speed"] = self.car_speed
                modified_graph.es[i]["travel_time"] = 0.125
            else:
                modified_graph.es[i]["speed"] = self.bike_speed
                modified_graph.es[i]["travel_time"] = 0.25
        return modified_graph

    def dilation(self, modified_graph_car, source, destination):
        """
        Calculate dilation using the original and modified graphs.
        Calculate the sum of time needed for both graphs (time = path length/speed)
        Dilation = time(modified)/time(original)
        """
        # return a list of edges that sum of time travel is lowest
        original_path = self.graph.get_shortest_path(source, to = destination, weights = self.graph.es["travel_time"], output = "epath")
        original_graph_cost = sum(self.graph.es[edge]["travel_time"] for edge in original_path)

        modified_path = modified_graph_car.get_shortest_path(source, to=destination, weights=modified_graph_car.es["travel_time"], output="epath")
        modified_cost = sum(modified_graph_car.es[edge]["travel_time"] for edge in modified_path)
        dilation = modified_cost/original_graph_cost

        return [dilation, modified_path]
    
    # def bike_dilation(self, modified_graph_bike, source, destination):
    #     original_path = self.graph.get_shortest_path(source, to = destination, weights = self.graph.es["travel_time"], output = "epath")
    #     original_graph_cost = sum(self.graph.es[edge]["travel_time"] for edge in original_path)

    #     bike_path = modified_graph_bike.get_shortest_path(source, to=destination, weights=modified_graph_bike.es["travel_time"], output="epath")
    #     bike_cost = sum(modified_graph_bike.es[edge]["travel_time"] for edge in bike_path)
    #     bike_dilation = bike_cost/original_graph_cost

    #     return bike_dilation

    def bruteForce(self, source, destination):
        car_optimized_dilation = float('inf')
        bike_optimized_dilation = float('inf')
        car_optimized_setting = None
        bike_optimized_setting = None

        bike_setting = ["bike"] * len(self.graph.es)

        modified_graph = self.getModifiedGraph(bike_setting)
        [bike_optimized_dilation, bike_optimized_setting]  = self.dilation(modified_graph, source, destination)


        car_setting = ["car"] * len(self.graph.es)
        for edge in bike_optimized_setting:
            car_setting[edge] = "bike"
        modified_graph = self.getModifiedGraph(car_setting)
        [car_optimized_dilation, car_optimized_setting]  = self.dilation(modified_graph, source, destination)

        print("\nBike Optimized Dilation:", bike_optimized_dilation)
        print("Bike Optimized Setting:", bike_optimized_setting)
        print("Car Optimized Dilation:", car_optimized_dilation)
        print("Car Optimized Setting:", car_optimized_setting)

        return [bike_optimized_dilation, bike_optimized_setting, car_optimized_dilation, car_optimized_setting]

        