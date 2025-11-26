"""
viz.py
Simple plotting helpers for maps and histograms.
"""
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np

def plot_hist_weighted(df, value_col='delta_min', weight_col='population', bins=50, title=None):
    # Expand by weights (careful with large numbers)
    vals = []
    for val, w in zip(df[value_col], df[weight_col]):
        if not np.isfinite(val) or w <= 0: 
            continue
        # sample-weighted approach: replicate up to cap
        cap = min(int(w), 1000)
        vals.extend([val] * cap)
    plt.hist(vals, bins=bins)
    plt.xlabel("Extra travel time (min)")
    plt.ylabel("Weighted count (capped)")
    if title:
        plt.title(title)

def plot_grid_map(grid_gdf, column='max_delta', ax=None, cmap='Reds', vmin=0, vmax=60):
    if ax is None:
        fig, ax = plt.subplots(1,1, figsize=(8,8))
    grid_gdf.plot(column=column, ax=ax, cmap=cmap, vmin=vmin, vmax=vmax, legend=True)
    ax.axis('off')
    return ax

