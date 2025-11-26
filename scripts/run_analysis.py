#!/usr/bin/env python3
"""
Small driver script to run the analysis pipeline.
Usage:
    python run_analysis.py --gtfs /path/to/gtfs.zip --grid /path/to/statec_grid.shp --walk 200
"""
import argparse
from src.gtfs_loader import load_gtfs, to_seconds
from src.graph_builder import build_base_graph, add_walking_edges
from src.analysis import compute_betweenness, select_top_hubs, precompute_baseline, compute_population_impact
import geopandas as gpd
import pandas as pd

def main(args):
    data = load_gtfs(args.gtfs)
    stops = data['stops']
    stop_times = data['stop_times']
    # convert times to seconds
    stop_times['arrival_time_seconds'] = stop_times['arrival_time'].apply(to_seconds)
    stop_times['departure_time_seconds'] = stop_times['departure_time'].apply(to_seconds)

    G = build_base_graph(stops, stop_times)
    print("Base graph:", G.number_of_nodes(), "nodes,", G.number_of_edges(), "edges")

    if args.walk > 0:
        G = add_walking_edges(G, stops, max_walk_m=args.walk)
        print("After walking edges:", G.number_of_edges(), "edges")

    bet = compute_betweenness(G, k=300)
    hubs = select_top_hubs(bet, top_n=5)
    print("Top hubs:", hubs)

    baseline = precompute_baseline(G, hubs)

    grid = gpd.read_file(args.grid)
    # compute centroids & nearest stops — naive approach, ensure CRS alignment in notebook
    grid = grid.to_crs(epsg=3035)
    stops_gdf = gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat), crs='EPSG:4326').to_crs(epsg=3035)
    # nearest mapping (simple)
    stops_sindex = stops_gdf.sindex
    nearest = []
    for idx, row in grid.iterrows():
        centroid = row.geometry.centroid
        possible = list(stops_sindex.nearest(centroid.bounds, num_results=1))
        if possible:
            nearest.append(stops_gdf.iloc[possible[0]]['stop_id'])
        else:
            nearest.append(None)
    grid['nearest_stop'] = nearest
    grid['population'] = grid.get('Pop_grids', grid.get('population', 0))

    impact_df = compute_population_impact(grid, baseline, G, hubs)
    impact_df.to_csv('impact_summary.csv', index=False)
    print("Saved impact_summary.csv")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--gtfs', required=True)
    p.add_argument('--grid', required=True)
    p.add_argument('--walk', type=int, default=200)
    args = p.parse_args()
    main(args)

