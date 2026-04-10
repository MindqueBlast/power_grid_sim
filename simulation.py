import random
import networkx as nx
from grid import update_loads

def fail_node(G, node):
    """Marks a node as failed."""
    if node in G and G.nodes[node]['status'] == 'active':
        G.nodes[node]['status'] = 'failed'
        G.nodes[node]['load'] = 0.0
        return True
    return False

def random_failure(G, num_failures=1):
    """Randomly fails a specified number of active nodes."""
    active_nodes = [n for n, attr in G.nodes(data=True) if attr['status'] == 'active']
    num_failures = min(num_failures, len(active_nodes))
    failed_nodes = random.sample(active_nodes, num_failures)
    
    for node in failed_nodes:
        fail_node(G, node)
    return failed_nodes

def targeted_attack(G, strategy="degree", num_failures=1):
    """
    Attacks nodes based on a centrality measure.
    strategy: 'degree', 'betweenness', 'eigenvector'
    """
    active_nodes = [n for n, attr in G.nodes(data=True) if attr['status'] == 'active']
    active_subgraph = G.subgraph(active_nodes)
    
    if len(active_nodes) == 0:
        return []

    if strategy == "degree":
        centrality = dict(active_subgraph.degree())
    elif strategy == "betweenness":
        centrality = nx.betweenness_centrality(active_subgraph, weight='weight')
    elif strategy == "eigenvector":
        try:
            centrality = nx.eigenvector_centrality_numpy(active_subgraph, weight='weight')
        except nx.NetworkXError:
            centrality = dict(active_subgraph.degree()) # Fallback
    else:
        raise ValueError("Unknown attack strategy")
    
    # Sort nodes by centrality
    sorted_nodes = sorted(centrality.keys(), key=lambda n: centrality[n], reverse=True)
    targets = sorted_nodes[:num_failures]
    
    for node in targets:
        fail_node(G, node)
        
    return targets

def simulate_cascade(G, max_steps=50):
    """
    Simulates cascading failures.
    Returns the sequence of state changes (number of failed nodes per step).
    """
    cascade_history = []
    
    for step in range(max_steps):
        # 1. Recompute loads for all active nodes based on new topology
        update_loads(G)
        
        # 2. Check for capacity violations
        newly_failed = []
        for node, attr in G.nodes(data=True):
            if attr['status'] == 'active':
                if attr['load'] > attr['power_capacity']:
                    newly_failed.append(node)
        
        # 3. Fail overloaded nodes
        for node in newly_failed:
            fail_node(G, node)
            
        # Record number of total active/failed nodes this step
        failed_count = sum(1 for n, d in G.nodes(data=True) if d['status'] == 'failed')
        cascade_history.append({
            'step': step,
            'newly_failed': len(newly_failed),
            'total_failed': failed_count
        })
        
        # 4. Stop if no new node failed
        if len(newly_failed) == 0:
            break
            
    return cascade_history
