from BollardOptimization import *

my_graph = BollardOptimization(3, 2, 40, 20)
my_graph.createGraph()

optimized_dilation, optimized_setting = my_graph.bruteForce(my_graph.graph.vs[0], my_graph.graph.vs[5])