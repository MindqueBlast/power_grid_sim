import streamlit as st
import matplotlib.pyplot as plt
from grid import generate_grid
from simulation import random_failure, targeted_attack, simulate_cascade
from analysis import calculate_metrics
from visualization import visualize_grid

st.set_page_config(page_title="Power Grid Simulator", layout="wide")

st.title("⚡ Power Grid Failure Simulator")
st.markdown("Simulate electrical power grids and analyze how cascading failures propagate.")

# Sidebar Settings
st.sidebar.header("Simulation Settings")

topology = st.sidebar.selectbox("Network Topology", ["scale-free", "small-world", "random"])
n_nodes = st.sidebar.slider("Number of Nodes", min_value=20, max_value=500, value=100, step=10)
tolerance = st.sidebar.slider("Capacity Tolerance (Alpha)", min_value=0.0, max_value=2.0, value=0.2, step=0.05)

st.sidebar.markdown("---")
st.sidebar.header("Attack Settings")
attack_strategy = st.sidebar.selectbox("Initial Attack Strategy", ["targeted_betweenness", "targeted_degree", "random"])
num_attack = st.sidebar.number_input("Nodes to Attack", min_value=1, max_value=max(1, n_nodes//2), value=max(1, min(2, n_nodes//2)), step=1)

if st.sidebar.button("Run Simulation", type="primary"):
    # Step 1: Generate Grid
    with st.spinner("Generating Grid..."):
        G = generate_grid(topology=topology, n_nodes=n_nodes, tolerance=tolerance)
        initial_metrics = calculate_metrics(G)
        
    st.subheader("1. Initial Network State")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**Pre-Attack Metrics:**")
        st.json(initial_metrics)
        
    with col2:
        fig_initial = visualize_grid(G, title=f"Initial Grid ({topology})", return_fig=True)
        st.pyplot(fig_initial)
        
    # Step 2: Apply Attack
    st.markdown("---")
    st.subheader(f"2. Applying {attack_strategy.replace('_', ' ').title()} Attack ({num_attack} nodes)")
    
    if attack_strategy == 'random':
        failed_nodes = random_failure(G, num_failures=num_attack)
    elif attack_strategy == 'targeted_degree':
        failed_nodes = targeted_attack(G, strategy='degree', num_failures=num_attack)
    elif attack_strategy == 'targeted_betweenness':
        failed_nodes = targeted_attack(G, strategy='betweenness', num_failures=num_attack)
        
    st.warning(f"Dynamically Failed Nodes: {failed_nodes}")
    fig_attack = visualize_grid(G, title="Grid After Initial Attack", return_fig=True)
    st.pyplot(fig_attack)
    
    # Step 3: Cascading Failures
    st.markdown("---")
    st.subheader("3. Simulating Cascading Failures")
    
    with st.spinner("Simulating physics cascade model..."):
        history = simulate_cascade(G)
    
    if len(history) == 0:
        st.info("No cascading failures occurred. Network absorbed the impact.")
    
    for step_info in history:
        with st.expander(f"Cascade Step {step_info['step'] + 1}", expanded=False):
            st.write(f"Newly failed nodes: **{step_info['newly_failed']}**")
            st.write(f"Total failed nodes: **{step_info['total_failed']}**")
            fig_step = visualize_grid(G, title=f"Step {step_info['step'] + 1} Cascade Status", return_fig=True)
            st.pyplot(fig_step)
            
    # Step 4: Final State
    st.markdown("---")
    st.subheader("4. Final Analysis")
    
    final_metrics = calculate_metrics(G)
    
    col3, col4 = st.columns([1, 2])
    with col3:
        st.write("**Post-Cascade Metrics:**")
        st.json(final_metrics)
        
    with col4:
        nodes_lost = final_metrics["total_nodes"] - final_metrics["active_nodes"]
        st.error(f"Total Nodes Offline: {nodes_lost} / {n_nodes}")
        st.info(f"Final Robustness (LCC/Total): {final_metrics['robustness']:.2%}")
        
        fig_final = visualize_grid(G, title="Final Grid State", return_fig=True)
        st.pyplot(fig_final)
