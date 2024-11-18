from BollardOptimization import *

my_graph = BollardOptimization(3, 3, 40, 20)

res = my_graph.bruteForce(my_graph.graph.vs[0], my_graph.graph.vs[5])