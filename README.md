# E-Scooter Trajectory Analysis – Chicago

This project analyzes e-scooter trips in Chicago, aggregates trip data, and generates visualizations including **trajectory maps**, **start/end point maps**, **hourly line charts**, **bar charts**, and **heatmaps**. The analysis is based on the official e-scooter dataset provided by the City of Chicago and OpenStreetMap road shapefiles.

---

## Project Structure

```
results/               # Output shapefiles, maps, charts
downloader.py          # Script to download datasets
start_end_map.py       # Creates aggregated start/end point maps
trajectory.py          # Generates trajectory maps
heatmap_creator.py     # Generates heatmaps of trips on roads
line_chart.py          # Creates hourly line charts
bar_chart.py           # Creates bar charts (weekdays vs weekends)
main.py                # Main pipeline to run all analyses
README.md              # Project documentation
```

---

## Requirements

* Python 3.9+
* Libraries:

  * `geopandas`
  * `pandas`
  * `matplotlib`
  * `shapely`
  * `networkx`
  * `geopy`
  * `tqdm`
  * `seaborn`

Install requirements via:

```bash
pip install -r requirements.txt
```

---

## Installation

1. Clone the repository

2. Install dependencies (see [Requirements](#requirements)).

3. Run:
```bash
python downloader.py
```

---

## Usage

Run the main pipeline:

```bash
python main.py e_scooter_trips.csv 01/04/2023 30/04/2023
```

**Arguments**:

* `e_scooter_trips.csv` – CSV file containing e-scooter trips.
* `01/04/2023` – Start date (dd/mm/yyyy).
* `30/04/2023` – End date (dd/mm/yyyy).

This will generate:

* Aggregated start/end maps
* Trajectory maps
* Heatmaps of road usage
* Hourly line charts
* Weekday/weekend bar charts

---

## Modules

### `downloader.py`

Downloads required datasets:

* E-scooter trips CSV from City of Chicago
* Illinois road shapefile

### `start_end_map.py`

Creates aggregated **start/end points maps** for a given date range.

### `trajectory.py`

Generates **trajectory maps** connecting start and end points of trips.

### `heatmap_creator.py`

Aggregates trips per road segment and generates **heatmaps** for weekdays/weekends and different providers (Lime, Lyft, Link).

### `line_chart.py`

Creates **hourly line charts** comparing weekday and weekend trips.

### `bar_chart.py`

Generates **bar charts** showing average trip duration for weekdays vs weekends.

### `main.py`

The main pipeline that calls all modules sequentially for a given CSV and date range.

---

## Outputs

All outputs are saved under `results/`:

* PNG maps and charts
* Shapefiles with aggregated counts per road segment

Example filenames:

```
01-04-2023_30-04-2023_points.png
01-04-2023_30-04-2023_trajectory_map.png
01-04-2023_30-04-2023_avg_ride_duration.png
01-04-2023_30-04-2023.shp
```