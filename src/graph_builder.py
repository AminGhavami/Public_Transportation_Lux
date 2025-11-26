"""
graph_builder.py
Build a directed weighted graph from GTFS (transit edges) and add walking-transfer edges.
"""

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree
import geopandas as gpd
from shapely.geometry import Point

WALK_SPEED_MPS = 1.33  # ~4.8 km/h

def build_base_graph(stops: pd.DataFrame, stop_times: pd.DataFrame) -> nx.DiGraph:
    G = nx.DiGraph()
    # add nodes
    for _, r in stops.iterrows():
        sid = r['stop_id']
        G.add_node(sid, name=r.get('stop_name'), lat=r.get('stop_lat'), lon=r.get('stop_lon'))
    # add transit edges
    for trip_id, group in stop_times.groupby('trip_id'):
        group = group.sort_values('stop_sequence')
        prev = None
        for _, row in group.iterrows():
            if prev is not None:
                u = prev['stop_id']; v = row['stop_id']
                try:
                    travel = float(row['arrival_time_seconds']) - float(prev['departure_time_seconds'])
                except:
                    travel = 60.0
                if travel <= 0:
                    travel = 60.0
                if G.has_edge(u, v):
                    # keep minimum (fastest) observed travel time
                    G[u][v]['weight'] = min(G[u][v]['weight'], travel)
                else:
                    G.add_edge(u, v, weight=travel, type='transit')
            prev = row
    return G

def add_walking_edges(G: nx.DiGraph, stops_df: pd.DataFrame, max_walk_m=200):
    """
    Add walking edges between stops within max_walk_m (meters).
    stops_df: dataframe with columns stop_id, stop_lat, stop_lon (EPSG:4326).
    """
    coords = np.deg2rad(stops_df[['stop_lat','stop_lon']].values)
    tree = BallTree(coords, metric='haversine')
    # convert radius degrees to radians using haversine: r_km / earth_radius_km
    earth_km = 6371.0088
    r = max_walk_m / 1000.0 / earth_km
    indices = tree.query_radius(coords, r=r)
    for i, neigh in enumerate(indices):
        u = stops_df.iloc[i]['stop_id']
        u_lat = stops_df.iloc[i]['stop_lat']; u_lon = stops_df.iloc[i]['stop_lon']
        for j in neigh:
            if i == j: 
                continue
            v = stops_df.iloc[j]['stop_id']
            # haversine distance in meters
            lat2 = stops_df.iloc[j]['stop_lat']; lon2 = stops_df.iloc[j]['stop_lon']
            d = haversine_m(u_lat, u_lon, lat2, lon2)
            walk_time = max(d / WALK_SPEED_MPS, 30.0)  # min 30s
            # add as directed edges both ways
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=walk_time, type='walk')
    return G

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1 = np.radians(lat1); phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1); dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2.0)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

