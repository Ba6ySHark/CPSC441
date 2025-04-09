import heapq
import json

class Searcher:
    def __init__(self, graph_data):
        self.graph = self.build_graph(graph_data)

    def build_graph(self, edges_data):
        graph = {}
        for edge in edges_data:
            src = edge["start"]
            dst = edge["end"]
            if src not in graph:
                graph[src] = []
            graph[src].append((dst, edge))
        return graph

    def dfs_paths(self, start, goal, path=None):
        if path is None:
            path = [start]
        if start == goal:
            yield path
        if start not in self.graph:
            return
        for (neighbor, _) in self.graph[start]:
            if neighbor not in path:  # avoid cycles
                yield from self.dfs_paths(neighbor, goal, path + [neighbor])

    def stp_dfs(self, start, goal):
        best_path = None
        best_time = float('inf')  # infinity by default
        for path in self.dfs_paths(start, goal):
            total_time = 0
            for i in range(len(path) - 1):
                for neighbor, edge in self.graph[path[i]]:
                    if neighbor == path[i + 1]:
                        total_time += edge["time"]
                        break
            if total_time < best_time:
                best_time = total_time
                best_path = path
        return best_path

    def fdp_dfs(self, start, goal):
        best_path = None
        best_dementors = float('inf')
        for path in self.dfs_paths(start, goal):
            total_dementors = 0
            for i in range(len(path) - 1):
                for neighbor, edge in self.graph[path[i]]:
                    if neighbor == path[i + 1]:
                        total_dementors += edge["dementors"]
                        break
            if total_dementors < best_dementors:
                best_dementors = total_dementors
                best_path = path
        return best_path

    def dijkstra(self, start, goal, weight_key="hops"):
        queue = [(0, start, [])]
        visited = set()

        while queue:
            cost, node, path = heapq.heappop(queue)
            if node == goal:
                return cost, path + [node]
            if node in visited:
                continue
            visited.add(node)
            for neighbor, edge in self.graph.get(node, []):
                new_cost = cost + edge[weight_key]
                heapq.heappush(queue, (new_cost, neighbor, path + [node]))
        return float('inf'), []

if __name__ == "__main__":
    alumni = {
        "Harry Potter": "British Columbia",
        "Hermione Granger": "Ontario",
        "Ron Weasley": "Quebec",
        "Luna Lovegood": "Newfoundland and Labrador",
        "Neville Longbottom": "Saskatchewan",
        "Ginny Weasley": "Nova Scotia"
    }

    destination = "Ottawa"

    with open("table.json", "r") as f:
        graph = json.load(f)
    searcher = Searcher(graph)

    print("\nOptimal Paths:\n")
    for name, start in alumni.items():
        print(f"For {name}:")
        
        # SHP using Dijkstra
        _, hop_path = searcher.dijkstra(start, destination, "hops")
        if hop_path:
            print(f"SHP: {' -> '.join(hop_path)}")
        else:
            print("SHP: No path found.")
        
        # SDP using Dijkstra
        _, dist_path = searcher.dijkstra(start, destination, "distance")
        if dist_path:
            print(f"SDP: {' -> '.join(dist_path)}")
        else:
            print("SDP: No path found.")
        
        # STP using DFS
        stp_path = searcher.stp_dfs(start, destination)
        if stp_path:
            print(f"STP: {' -> '.join(stp_path)}")
        else:
            print("STP: No path found.")
        
        # FDP using DFS
        fdp_path = searcher.fdp_dfs(start, destination)
        if fdp_path:
            print(f"FDP: {' -> '.join(fdp_path)}")
        else:
            print("FDP: No path found.")
            
        print("\n")