import networkx as nx

def calculate_metrics(G):
    """
    Computes key analysis metrics for the current state of the grid.
    """
    active_nodes = [n for n, attr in G.nodes(data=True) if attr['status'] == 'active']
    active_subgraph = G.subgraph(active_nodes)
    
    total_nodes = G.number_of_nodes()
    failed_count = total_nodes - len(active_nodes)
    
    # Largest connected component (LCC)
    if len(active_nodes) > 0:
        components = list(nx.connected_components(active_subgraph))
        lcc_size = len(max(components, key=len)) if components else 0
    else:
        lcc_size = 0
        
    # Robustness (fraction of nodes in LCC compared to original graph size)
    robustness = lcc_size / total_nodes if total_nodes > 0 else 0
    
    # Network Efficiency
    if len(active_nodes) > 1:
        try:
            # Global efficiency is average inverse shortest path length
            efficiency = nx.global_efficiency(active_subgraph)
        except Exception:
            efficiency = 0
    else:
        efficiency = 0
        
    # Calculate some summary centralities (averages)
    avg_degree = sum(dict(active_subgraph.degree()).values()) / len(active_nodes) if len(active_nodes) > 0 else 0
        
    metrics = {
        'total_nodes': total_nodes,
        'active_nodes': len(active_nodes),
        'failed_nodes': failed_count,
        'lcc_size': lcc_size,
        'robustness': float(robustness),
        'efficiency': float(efficiency),
        'average_degree': float(avg_degree)
    }
    
    return metrics

def print_metrics(metrics):
    """Pretty prints the metrics dictionary."""
    print("--- Network Metrics ---")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key.replace('_', ' ').title()}: {value:.4f}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    print("-----------------------\n")
