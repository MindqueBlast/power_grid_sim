import argparse
import os
from grid import generate_grid
from simulation import random_failure, targeted_attack, simulate_cascade
from analysis import calculate_metrics, print_metrics
from visualization import visualize_grid

def parse_args():
    parser = argparse.ArgumentParser(description="Power Grid Failure Simulator")
    parser.add_argument('--topology', type=str, default='scale-free', choices=['random', 'small-world', 'scale-free'],
                        help="Network topology type")
    parser.add_argument('--nodes', type=int, default=100, help="Number of nodes in the grid")
    parser.add_argument('--tolerance', type=float, default=0.2, 
                        help="Capacity tolerance. higher means a grid can absorb more extra load.")
    parser.add_argument('--attack', type=str, default='targeted_degree', choices=['random', 'targeted_degree', 'targeted_betweenness'],
                        help="Type of initial attack/failure")
    parser.add_argument('--num_attack', type=int, default=2, help="Number of nodes to fail initially")
    parser.add_argument('--output_dir', type=str, default='./output', help="Directory to save plots")
    return parser.parse_args()

def main():
    args = parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Generating {args.topology} grid with {args.nodes} nodes and tolerance {args.tolerance}...")
    G = generate_grid(topology=args.topology, n_nodes=args.nodes, tolerance=args.tolerance)
    
    print("\nInitial State Metrics:")
    metrics = calculate_metrics(G)
    print_metrics(metrics)
    
    visualize_grid(G, title=f"Initial Grid ({args.topology})", filename=os.path.join(args.output_dir, "step_0_initial.png"))
    
    print(f"Applying initial failure ({args.attack}, amount: {args.num_attack})...")
    if args.attack == 'random':
        failed = random_failure(G, num_failures=args.num_attack)
    elif args.attack == 'targeted_degree':
        failed = targeted_attack(G, strategy='degree', num_failures=args.num_attack)
    elif args.attack == 'targeted_betweenness':
        failed = targeted_attack(G, strategy='betweenness', num_failures=args.num_attack)
        
    print(f"Nodes dynamically failed: {failed}")
    visualize_grid(G, title="After Initial Attack", filename=os.path.join(args.output_dir, "step_1_attacked.png"))
    
    print("\nSimulating Cascading Failures...")
    history = simulate_cascade(G)
    
    for step_info in history:
        print(f"Cascade Step {step_info['step']}: {step_info['newly_failed']} newly failed, Total Failed: {step_info['total_failed']}")
        # Save visualization for each cascade iteration
        visualize_grid(G, title=f"Cascade Step {step_info['step']}", 
                       filename=os.path.join(args.output_dir, f"step_{step_info['step'] + 2}_cascade.png"))
    
    print("\nFinal State Metrics:")
    final_metrics = calculate_metrics(G)
    print_metrics(final_metrics)
    
    visualize_grid(G, title="Final Grid State", filename=os.path.join(args.output_dir, "step_final.png"))
    
    print(f"\nSimulation complete. Visualizations saved to '{args.output_dir}'")

if __name__ == '__main__':
    main()
