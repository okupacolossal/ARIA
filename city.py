import osmnx as ox

graph = ox.graph_from_place("Porto, Portugal", network_type="drive")

print(type(graph))
print(f"nodes: {graph.number_of_nodes()}")
print(f"edges: {graph.number_of_edges()}")

node_id = list(graph.nodes)[0]
print(f"\nfirst node id: {node_id}")
print(f"first node data: {graph.nodes[node_id]}")