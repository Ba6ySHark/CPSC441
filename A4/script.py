import json
import os
import heapq
import networkx as nx
import matplotlib.pyplot as plt

# ============================
# 1. Load the Table of Magical Paths from an External JSON File
# ============================
json_file = "table.json"

# Check if the JSON file exists.
if not os.path.exists(json_file):
    print(f"Error: {json_file} not found. Ensure the file is in the same directory as this script.")
    exit(1)

with open(json_file, "r") as f:
    magical_paths = json.load(f)

# ============================
# 2. Build the Graph from the Loaded Data
# ============================
def build_graph(edges_data):
    """
    Build a graph represented as a dictionary where each starting province maps
    to a list of (destination, edge data) tuples.
    """
    graph = {}
    for edge in edges_data:
        src = edge["start"]
        dst = edge["end"]
        if src not in graph:
            graph[src] = []
        graph[src].append((dst, edge))
    return graph

graph = build_graph(magical_paths)

# ============================
# 3. DFS for Shortest Hop Path (Fewest Connections)
# ============================
def dfs_paths(graph, start, goal, path=None):
    """
    A generator function that yields all possible simple paths from start to goal.
    """
    if path is None:
        path = [start]
    if start == goal:
        yield path
    if start not in graph:
        return
    for (neighbor, _) in graph[start]:
        if neighbor not in path:  # avoid cycles
            yield from dfs_paths(graph, neighbor, goal, path + [neighbor])

def shortest_hop_path_dfs(graph, start, goal):
    """
    Returns the path with the fewest connections (i.e. edges) using DFS.
    """
    best_path = None
    for path in dfs_paths(graph, start, goal):
        if best_path is None or len(path) < len(best_path):
            best_path = path
    return best_path

# ============================
# 4. Dijkstra’s Algorithm for Weighted Paths
# ============================
def dijkstra(graph, start, goal, weight_key):
    """
    Generic implementation of Dijkstra's algorithm.
    weight_key should be one of "distance", "time", or "dementors".
    Returns a tuple: (total_weight, optimal_path).
    """
    # Priority queue: (cost, current_node, path_taken)
    queue = [(0, start, [])]
    visited = set()
    
    while queue:
        cost, node, path = heapq.heappop(queue)
        if node == goal:
            return cost, path + [node]
        if node in visited:
            continue
        visited.add(node)
        for neighbor, edge in graph.get(node, []):
            new_cost = cost + edge[weight_key]
            heapq.heappush(queue, (new_cost, neighbor, path + [node]))
    return float('inf'), []

# ============================
# 5. Evaluate and Print the Optimal Paths for Each Alumnus
# ============================
# List of alumni with their starting provinces.
alumni = {
    "Harry Potter": "British Columbia",
    "Hermione Granger": "Ontario",
    "Ron Weasley": "Quebec",
    "Luna Lovegood": "Newfoundland and Labrador",
    "Neville Longbottom": "Saskatchewan",
    "Ginny Weasley": "Nova Scotia"
}

destination = "Ottawa"

print("\nOptimal Paths from each alumnus' location to Ottawa:\n")
for name, start in alumni.items():
    print(f"--- {name} (from {start}) ---")
    
    # Shortest Hop Path using DFS.
    hop_path = shortest_hop_path_dfs(graph, start, destination)
    if hop_path:
        print("Shortest Hop Path (fewest connections):", " -> ".join(hop_path))
    else:
        print("No path found using DFS for Shortest Hop Path.")

    # Shortest Distance Path using Dijkstra's algorithm.
    dist_cost, dist_path = dijkstra(graph, start, destination, "distance")
    if dist_path:
        print("Shortest Distance Path:", " -> ".join(dist_path), f"(Total Distance: {dist_cost} km)")
    else:
        print("No path found for Shortest Distance Path.")
    
    # Shortest Time Path using Dijkstra's algorithm.
    time_cost, time_path = dijkstra(graph, start, destination, "time")
    if time_path:
        print("Shortest Time Path:", " -> ".join(time_path), f"(Total Time: {time_cost} hrs)")
    else:
        print("No path found for Shortest Time Path.")
    
    # Fewest Dementors Path using Dijkstra's algorithm.
    dem_cost, dem_path = dijkstra(graph, start, destination, "dementors")
    if dem_path:
        print("Fewest Dementors Path:", " -> ".join(dem_path), f"(Total Dementors: {dem_cost})")
    else:
        print("No path found for Fewest Dementors Path.")
        
    print()

# ============================
# 6. Visualize the Magical Transportation Network
# ============================
# Create a directed graph using NetworkX.
G = nx.DiGraph()
for src in graph:
    for dst, edge in graph[src]:
        G.add_edge(src, dst, distance=edge["distance"], time=edge["time"], dementors=edge["dementors"])

plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', arrowstyle='->', arrowsize=12)

# Use the distance metric as edge labels for demonstration.
edge_labels = nx.get_edge_attributes(G, 'distance')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.title("Magical Transportation Network (Edge labels = Distance in km)")
plt.show()
