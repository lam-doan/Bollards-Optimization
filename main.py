from BollardOptimization import *

bo = BollardOptimization(40, 20)
my_graph = bo.graph
print(list(my_graph.vs()))

source_id = 122628600
destination_id = 1494035566 
source_index = None
destination_index = None

for index, node in enumerate(my_graph.vs):
    if node["osm_ID"] == source_id:
        source_index = index
    if node["osm_ID"] == destination_id:
        destination_index = index

if source_index is None or destination_index is None:
    raise ValueError("Source or Destination node not found in the graph.")

res = bo.bruteForce(source_index, destination_index)

print("Best Maximum Dilation:", res[0])
print("Best Edge Settings:", res[1])