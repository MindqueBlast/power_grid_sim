import networkx as nx
import random
import numpy as np

def generate_grid(topology="scale-free", n_nodes=100, tolerance=0.2):
    """
    Generates a synthetic power grid network.
    
    Args:
        topology (str): "random", "small-world", or "scale-free"
        n_nodes (int): Number of nodes in the grid
        tolerance (float): Capacity tolerance (alpha). Capacity = (1 + alpha) * initial_load
        
    Returns:
        nx.Graph: The generated power grid
    """
    if topology == "random":
        # Erdős-Rényi random graph
        G = nx.erdos_renyi_graph(n=n_nodes, p=0.05)
    elif topology == "small-world":
        # Watts-Strogatz small-world graph (k=4 neighbors, p=0.1 rewiring probability)
        # Using connected_watts_strogatz_graph to ensure it's fully connected
        G = nx.connected_watts_strogatz_graph(n=n_nodes, k=4, p=0.1, tries=100)
    elif topology == "scale-free":
        # Barabási-Albert scale-free graph
        G = nx.barabasi_albert_graph(n=n_nodes, m=2)
    else:
        raise ValueError("Invalid topology. Choose 'random', 'small-world', or 'scale-free'.")
    
    # Ensure the graph is connected. If not, only take the largest connected component.
    if not nx.is_connected(G):
        largest_cc = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest_cc).copy()
        
    # Initialize basic edge weights (resistance/distance)
    for u, v in G.edges():
        G.edges[u, v]['weight'] = random.uniform(0.5, 2.0)
        G.edges[u, v]['transmission_capacity'] = random.uniform(50, 200)

    # Initialize nodes
    # We use betweenness centrality as an approximation for normal power flow load
    initial_loads = nx.betweenness_centrality(G, weight='weight', normalized=True)
    
    for node in G.nodes():
        load = initial_loads[node]
        # In case betweenness is 0, give a tiny baseline load to avoid 0 capacity
        load = load if load > 0 else 0.001
        capacity = load * (1.0 + tolerance)
        
        G.nodes[node]['load'] = load
        G.nodes[node]['power_capacity'] = capacity
        G.nodes[node]['status'] = 'active'  # 'active' or 'failed'
        
    return G

def update_loads(G):
    """
    Recomputes loads based on the current active topology.
    Nodes with 'failed' status are ignored for shortest paths.
    """
    # Create subgraph of only active nodes
    active_nodes = [n for n, attr in G.nodes(data=True) if attr['status'] == 'active']
    active_subgraph = G.subgraph(active_nodes)
    
    # Calculate new loads based on betweenness centrality
    new_loads = nx.betweenness_centrality(active_subgraph, weight='weight', normalized=True)
    
    # Update loads in the main graph
    for node in active_nodes:
        G.nodes[node]['load'] = new_loads[node]
