# This program is optimised for the PyCharm environment

import networkx as nx
import matplotlib.pyplot as plt

# Create a graph object
MyGraph = nx.Graph()

# Add nodes
# Green Line
MyGraph.add_node('A', npos=(10, 10), ccn='#00FF00')
MyGraph.add_node('B', npos=(50, 50), ccn='#00FF00')
MyGraph.add_node('C', npos=(50, 90), ccn='#00FF00')
MyGraph.add_node('D', npos=(75, 90), ccn='#00FF00')
# Orange Line
MyGraph.add_node('E', npos=(55, 50), ccn='#FF4500')
MyGraph.add_node('F', npos=(90, 90), ccn='#FF4500')
MyGraph.add_node('G', npos=(175, 90), ccn='#FF4500')
MyGraph.add_node('H', npos=(175, 70), ccn='#FF4500')
# Blue Line
MyGraph.add_node('I', npos=(150, 25), ccn='#0000FF')
MyGraph.add_node('J', npos=(130, 55), ccn='#0000FF')
MyGraph.add_node('K', npos=(100, 65), ccn='#0000FF')
MyGraph.add_node('L', npos=(52, 45), ccn='#0000FF')

# Connect the Green Line
MyGraph.add_edge('A', 'B', cce='#00FF00')
MyGraph.add_edge('B', 'C', cce='#00FF00')
MyGraph.add_edge('C', 'D', cce='#00FF00')

# Connect the Orange Line
MyGraph.add_edge('E', 'F', cce='#FF4500')
MyGraph.add_edge('F', 'G', cce='#FF4500')
MyGraph.add_edge('G', 'H', cce='#FF4500')

# Connect the Blue Line
MyGraph.add_edge('I', 'J', cce='#0000FF')
MyGraph.add_edge('J', 'K', cce='#0000FF')
MyGraph.add_edge('K', 'L', cce='#0000FF')

# Extract attributes from the graph to dictionaries
pos = nx.get_node_attributes(MyGraph, 'npos')
nodecolour = nx.get_node_attributes(MyGraph, 'ccn')
edgecolour = nx.get_edge_attributes(MyGraph, 'cce')

# Place the dictionary values in array
nodearray = nodecolour.values()
edgearray = edgecolour.values()

plt.figure(figsize=(10, 7))

# Display the name of the stations
plt.text(15, 10, s='Green Station 1', rotation=15)
plt.text(32, 45, s='Station', rotation=15)
plt.text(20, 83, s='Green Station 2', rotation=15)
plt.text(54, 80, s='Green Station 3', rotation=15)

plt.text(85, 77, s='Orange Station 1', rotation=15)
plt.text(143, 80, s='Orange Station 2', rotation=15)
plt.text(143, 62, s='Orange Station 3', rotation=15)

plt.text(122, 18, s='Blue Station 1', rotation=15)
plt.text(100, 48, s='Blue Station 2', rotation=15)
plt.text(105, 65, s='Blue Station 3', rotation=15)

# Draw the graph's nodes and edges
nx.draw_networkx(MyGraph, pos, node_color=nodearray)
nx.draw_networkx_edges(MyGraph, pos, edge_color=edgearray)

# Visualise the graph
plt.show()