"""
analysis.py
Compute centrality, select hubs, simulate failures, compute population exposure metrics.
"""

import networkx as nx
import numpy as np
import pandas as pd
from typing import List, Dict

def compute_betweenness(G, k: int = None):
    # if k is None, compute exact; otherwise approximate
    if k is None:
        return nx.betweenness_centrality(G, weight='weight', normalized=True)
    else:
        return nx.betweenness_centrality(G, k=k, weight='weight', normalized=True)

def select_top_hubs(betweenness: Dict, top_n=5) -> List:
    sorted_nodes = sorted(betweenness.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nodes[:top_n]]

def precompute_baseline(G, hubs: List):
    baseline = {}
    for hub in hubs:
        # single_target_shortest_path_length returns distances from all nodes to hub
        try:
            d = nx.single_target_shortest_path_length(G, hub, weight='weight')
        except:
            d = {}
        baseline[hub] = d
    return baseline

def simulate_node_removal(G, node):
    G2 = G.copy()
    if node in G2:
        G2.remove_node(node)
    return G2

def compute_population_impact(grid_gdf, baseline_dict, G, hubs):
    """
    grid_gdf must have columns: nearest_stop (stop_id), population (int)
    baseline_dict: precomputed mapping hub-> {stop:dist}
    returns DataFrame of impacts: columns [cell_index, population, hub, delta_min]
    """
    rows = []
    for idx, row in grid_gdf.iterrows():
        s = row['nearest_stop']
        pop = int(row.get('population', 0))
        if s is None:
            continue
        # baseline to nearest hub
        base_times = [baseline_dict.get(h, {}).get(s, np.inf) for h in hubs]
        base = np.nanmin(base_times)
        if not np.isfinite(base):
            continue
        for hub in hubs:
            G_failed = simulate_node_removal(G, hub)
            alt_times = []
            for h2 in hubs:
                if h2 == hub: continue
                try:
                    alt_times.append(nx.shortest_path_length(G_failed, s, h2, weight='weight'))
                except:
                    pass
            alt = np.min(alt_times) if alt_times else np.inf
            delta_min = (alt - base) / 60.0 if np.isfinite(alt) else np.inf
            rows.append({"cell": idx, "population": pop, "failed_hub": hub, "delta_min": delta_min})
    return pd.DataFrame(rows)

