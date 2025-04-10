import osmnx as ox

area_name = "Fullerton, California, USA"
graph_networkx = ox.graph_from_place(area_name, network_type='all')
#print(graph_networkx.edges(keys=True, data=True))
print(graph_networkx.nodes(data=True))

