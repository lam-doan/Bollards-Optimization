from BollardOptimization import *

bo = BollardOptimization(40, 20)
my_graph = bo.graph

source_id = 122613066
destination_id = 122628602
source_index = None
destination_index = None

for index, node in enumerate(my_graph.vs):
    if node["osm_ID"] == source_id:
        source_index = index
        print("Start point:", source_index)
    if node["osm_ID"] == destination_id:
        destination_index = index
        print("Destination point:", destination_index)

if source_index is None or destination_index is None:
    raise ValueError("Source or Destination node not found in the graph.")

res = bo.searchOptimization(source_index, destination_index)