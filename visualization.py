import matplotlib.pyplot as plt
import networkx as nx
import os

def visualize_grid(G, title="Power Grid", filename=None):
    """
    Visualizes the current state of the grid.
    Active nodes are green, failed nodes are red.
    """
    plt.figure(figsize=(10, 8))
    
    # Generate layout if not already computed
    if not hasattr(G, 'pos') or getattr(G, 'pos') is None:
        G.pos = nx.spring_layout(G, seed=42)
        
    active_nodes = [n for n, d in G.nodes(data=True) if d['status'] == 'active']
    failed_nodes = [n for n, d in G.nodes(data=True) if d['status'] == 'failed']
    
    # Draw edges
    # We can draw active edges vs inactive edges
    active_subgraph = G.subgraph(active_nodes)
    active_edges = active_subgraph.edges()
    
    pos = G.pos
    
    # Draw all edges lightly
    nx.draw_networkx_edges(G, pos, alpha=0.1, edge_color='gray')
    # Draw active edges darker
    nx.draw_networkx_edges(G, pos, edgelist=active_edges, alpha=0.5, edge_color='blue')
    
    # Draw nodes
    node_size = 150
    nx.draw_networkx_nodes(G, pos, nodelist=active_nodes, node_color='green', node_size=node_size, label="Active", edgecolors='black')
    
    if failed_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=failed_nodes, node_color='red', node_size=node_size, label="Failed", edgecolors='black')
    
    plt.title(title, fontsize=16)
    plt.axis('off')
    
    # Ensure legend is shown without duplicates
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    
    if filename:
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()
    else:
        plt.show()
