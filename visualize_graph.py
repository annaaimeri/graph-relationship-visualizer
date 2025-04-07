#!/usr/bin/env python3
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import os

if len(sys.argv) > 1:
    json_file_path = sys.argv[1]
else:
    json_file_path = os.path.join(os.path.dirname(__file__), "example_graph.json")

if not os.path.exists(json_file_path):
    print(f"Error: The file '{json_file_path}' does not exist.")
    print("Please create a JSON file with the graph data or specify the correct path.")
    print("Usage: python visualize_graph.py [path_to_file.json]")
    sys.exit(1)

try:
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
except json.JSONDecodeError:
    print(f"Error: The file '{json_file_path}' does not contain valid JSON format.")
    sys.exit(1)
except Exception as e:
    print(f"Error reading the file: {e}")
    sys.exit(1)

# Create a directed graph
G = nx.DiGraph()

# Map IDs to names for easier visualization
id_to_name = {}
node_types = {}
node_levels = {}

# Add nodes
for node in data["nodes"]:
    id_to_name[node["id"]] = node["name"]
    node_types[node["id"]] = node["type"]
    G.add_node(node["id"])
    if "level" in node:
        node_levels[node["id"]] = node["level"]
    elif "isCentral" in node and node["isCentral"]:
        node_levels[node["id"]] = 0

# Add edges
for edge in data["edges"]:
    relationship = edge.get("relationship", "")
    G.add_edge(edge["source"], edge["target"], relationship=relationship)

# Configure the graph layout 
pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

plt.figure(figsize=(14, 10))

node_colors = {
    "Account": "skyblue",
    "Contact": "lightgreen"
}

# Sizes by level
node_sizes = {
    0: 2000,  # Central
    1: 1500,  # Level 1
    2: 1000   # Level 2
}

# Draw nodes
for node_type in set(node_types.values()):
    nodes_of_type = [node for node, type_val in node_types.items() if type_val == node_type]
    node_size = [node_sizes.get(node_levels.get(node, 1), 800) for node in nodes_of_type]
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=nodes_of_type,
                          node_color=node_colors.get(node_type, "gray"),
                          node_size=node_size,
                          alpha=0.8,
                          label=node_type)

# Draw edges with relationship labels
edge_labels = {(u, v): d.get('relationship', '') for u, v, d in G.edges(data=True)}
nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, edge_color='gray', 
                       connectionstyle='arc3,rad=0.1', arrowsize=15)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

# Add node labels with real names
labels = {node: id_to_name[node] for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight="bold")

account_patch = mpatches.Patch(color=node_colors.get("Account"), label='Account')
contact_patch = mpatches.Patch(color=node_colors.get("Contact"), label='Contact')
plt.legend(handles=[account_patch, contact_patch], loc='upper right')

# Configure layout
plt.title("Relationship Network", fontsize=16)
plt.axis('off')  # Hide axes

# Save image
plt.tight_layout()
plt.savefig('graph_visualization.png', dpi=300, bbox_inches='tight')
print(f"Graph saved as 'graph_visualization.png'")

plt.show()