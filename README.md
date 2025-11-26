# Public_Transportation_Lux

Analysis of Luxembourg public transportation network using GTFS(20251119-20251231) schedules.

## Overview

This repo contains:
- an interactive Jupyter notebook (`notebooks/Lux_Transport.ipynb`) used for exploration and results;
- modular Python code under `src/` for loading GTFS, building a transit+walking graph, computing centrality, simulating failures, and plotting results;
- a small CLI script to run the full pipeline.

Key idea: add walking-transfer edges between stops within a threshold (e.g., 200–400 m) and evaluate how removing hubs or services affects travel times and population exposure (STATEC 1km grid).

## Repo structure

Public_Transportation_Lux/\
├─ notebooks/\
│ └─ Lux_transport.ipynb\
├─ src/  
│ ├─ gtfs_loader.py\
│ ├─ graph_builder.py\
│ ├─ analysis.py\
│ └─ viz.py\
├─ scripts/\
│ └─ run_analysis.py\
├─ data/ # NOT included in repo; put GTFS zip and STATEC shapefiles here\
├─ requirements.txt\
└─ README.md\


## Quickstart

1. Create a virtual environment and install dependencies:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


2. Place GTFS zip (e.g., `gtfs-luxembourg.zip`) and STATEC grid shapefile into `data/`.

3. Run the analysis (CLI):

```
python scripts/run_analysis.py --gtfs data/gtfs-luxembourg.zip --grid data/statec_grid.shp --walk 200
```


Or open `notebooks/Transport_clean.ipynb` and run interactively.

## License

This Repo prepared for Data Science course, Supervised by Prof. Christophe Ley, and presented on Nov. 2025 at University of Luxembourg
