"""
gtfs_loader.py
Utilities to load GTFS (static) into pandas DataFrames.
"""

import pandas as pd
import gtfs_kit as gk
from typing import Dict

def load_gtfs(gtfs_zip_path: str) -> Dict[str, pd.DataFrame]:
    """
    Load GTFS feed using gtfs_kit (preferred) if available, otherwise fallback to pandas.
    Returns a dict with keys: stops, stop_times, trips, routes
    """
    try:
        feed = gk.read_feed(gtfs_zip_path, dist_units='km')
        stops = feed.stops.copy()
        stop_times = feed.stop_times.copy()
        trips = feed.trips.copy()
        routes = feed.routes.copy()
        return {"stops": stops, "stop_times": stop_times, "trips": trips, "routes": routes}
    except Exception as e:
        # Fallback: direct CSV reading if gtfs_zip_path is unzipped folder
        import zipfile
        import io
        with zipfile.ZipFile(gtfs_zip_path) as z:
            def _read_csv(fname):
                if fname in z.namelist():
                    return pd.read_csv(z.open(fname))
                return pd.DataFrame()
            stops = _read_csv('stops.txt')
            stop_times = _read_csv('stop_times.txt')
            trips = _read_csv('trips.txt')
            routes = _read_csv('routes.txt')
            return {"stops": stops, "stop_times": stop_times, "trips": trips, "routes": routes}

def to_seconds(hms):
    if pd.isna(hms):
        return None
    hms = str(hms).strip()
    parts = hms.split(':')
    if len(parts) == 2:
        parts = ['0'] + parts
    h, m, s = (int(x) for x in parts)
    return h * 3600 + m * 60 + s

