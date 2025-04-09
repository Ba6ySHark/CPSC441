import json
import networkx as nx
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, graph_data):
        self.graph = self.build_graph(graph_data)

    def build_graph(self, edges_data):
        graph = nx.DiGraph()
        for edge in edges_data:
            src = edge["start"]
            dst = edge["end"]
            graph.add_edge(src, dst, distance=edge["distance"], time=edge["time"], dementors=edge["dementors"])
        return graph

    def visualize(self):
        pos = nx.spring_layout(self.graph, seed=42, k=0.25)  # Note: 'k' is the distance between nodes (the lower the better)

        plt.figure(figsize=(42, 42))

        nx.draw_networkx_nodes(self.graph, pos, node_size=2000, node_color='lightblue', alpha=0.7)
        nx.draw_networkx_edges(self.graph, pos, width=2, alpha=0.5, edge_color='gray')

        nx.draw_networkx_labels(self.graph, pos, font_size=8, font_weight='bold', font_color='black')
        
        edge_labels = {(u, v): f"Dist: {d['distance']} km\nTime: {d['time']} hrs\nDementors: {d['dementors']}" 
                       for u, v, d in self.graph.edges(data=True)}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8, font_weight='bold')

        plt.title("Magical Network Visualization", fontsize=16)
        plt.axis('off')
        plt.show()


if __name__ == "__main__":
    with open("table.json", "r") as f:
        graph_data = json.load(f)
    visualizer = Visualizer(graph_data)
    visualizer.visualize()
