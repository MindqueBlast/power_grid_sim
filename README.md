# Power Grid Failure Simulator ⚡

A Python-based simulation tool using `NetworkX` to model electrical power grids and analyze how failures propagate through infrastructure networks.

## Table of Contents
- [Problem Motivation](#problem-motivation)
- [Graph Theory Concepts](#graph-theory-concepts)
- [How Cascading Failures Work](#how-cascading-failures-work)
- [Installation](#installation)
- [Usage](#usage)
- [Simulation Experiments](#simulation-experiments)
- [Project Structure](#project-structure)

## Problem Motivation
Modern power grids are complex, highly interconnected networks. While this interconnection provides robustness to common perturbations, it also creates vulnerabilities where local failures (like a power station going offline or a transmission line severing) can redistribute load onto neighboring components, causing them to overload and fail, triggering a catastrophic **cascading blackout**. Understanding and simulating these vulnerabilities is crucial for designing resilient infrastructure.

## Graph Theory Concepts
In this simulation, the power grid is modeled as a mathematical graph:
- **Nodes (Vertices):** Represent power stations, substations, or consumption hubs.
- **Edges (Lines):** Represent transmission lines connecting nodes.
- **Node Attributes:** `power_capacity` (maximum tolerable load), `load` (current operational stress levels), and `status` (active or failed).
- **Edge Attributes:** `transmission_capacity` and `weight` (resistance/distance). 

Different topologies can be generated to model different realities:
- **Random Graphs (Erdős-Rényi):** Baseline probabilistic connections.
- **Small-World (Watts-Strogatz):** High clustering with short path lengths, common in localized infrastructural hubs.
- **Scale-Free (Barabási-Albert):** Characterized by "hubs" (a few nodes with extremely high connectivity). Real-world grids often exhibit scale-free properties.

## How Cascading Failures Work
Our simulation utilizes standard load-capacity models (inspired by Motter and Lai, 2002):
1. **Initial Flow:** The network operates in steady state. `load` is estimated by the node's **Betweenness Centrality** (the proportion of shortest paths that pass through it).
2. **Capacity:** Each node's capacity is proportional to its initial load: `Capacity = Load * (1 + tolerance)`. The `tolerance` dictates how much extra power a node can handle.
3. **Attack / Failure:** Nodes are removed via random failure or targeted attack (e.g., knocking out high-degree hubs).
4. **Load Redistribution:** Shortest paths in the graph change as nodes drop. The system re-evaluates the load across all remaining active nodes.
5. **Overload & Cascade:** If a new redistributed load exceeds a node's capacity, that node fails, triggering another round of redistribution. This process iterates until no further nodes fail.

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/Mac: source venv/bin/activate
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

You can run the simulation from the command line:

```bash
python main.py
```

### Adjustable Parameters:
- `--topology`: Network type (`random`, `small-world`, `scale-free`). Defaults to `scale-free`.
- `--nodes`: Number of nodes. Defaults to 100.
- `--tolerance`: The extra percentage load a node can handle. Defaults to 0.2 (20%).
- `--attack`: Initial failure strategy (`random`, `targeted_degree`, `targeted_betweenness`). Defaults to `targeted_degree`.
- `--num_attack`: Number of initial failures. Defaults to 2.
- `--output_dir`: Path to save visualization steps. Defaults to `./output`.

### Example Run
Run a small-world network with 200 nodes and attack the highest betweenness node:
```bash
python main.py --topology small-world --nodes 200 --tolerance 0.3 --attack targeted_betweenness --num_attack 1
```

## Simulation Experiments
By altering standard arguments, you can simulate multiple scenarios:
- **Random Degradation:** Simulate general component aging or unpredictable weather events by attacking randomly.
- **Targeted Sabotage:** Target highest-degree or highest-betweenness nodes to observe infrastructure vulnerability against malicious attacks.
- **Robustness Comparison:** Compare how a Small-World topology handles targeted attacks versus a Scale-Free topology.

Key metrics outputted at the end include the `Robustness Score` (fraction of nodes still connected in the largest component) and `Network Efficiency`.

## Project Structure
- `main.py` - Command-line interface and simulation lifecycle.
- `grid.py` - Handles creation of topologies and initial load/capacity allocations.
- `simulation.py` - Manages attack strategies and the cascading failure loop.
- `analysis.py` - Computes connectivity and centrality metrics.
- `visualization.py` - Generates images of grid states across time steps.
