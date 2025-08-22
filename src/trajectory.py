import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from datetime import datetime
from tqdm import tqdm
from collections import defaultdict


def read_trips_file(filename, start_date=None, end_date=None):
    """
    Reads a CSV file containing trip data, filters by date and geographic bounds,
    and returns a DataFrame with valid trips.

    Parameters
    ----------
    filename : str
        Path to the CSV file containing trip data.
    start_date : datetime, optional
        Start of the date range for filtering trips (inclusive).
    end_date : datetime, optional
        End of the date range for filtering trips (inclusive).

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns: start_time, end_time, start_latitude, start_longitude,
        end_latitude, end_longitude.
    """
    # Define geographic boundaries (Chicago area) with margin
    margin = 0.1
    lon_min = -87.89370076 - margin
    lon_max = -87.5349023379022 + margin
    lat_min = 41.66013746994182 - margin
    lat_max = 42.00962338 + margin

    trips = []

    # Count total lines for progress bar
    number_of_lines = sum(1 for _ in open(filename))
    with open(filename, 'r') as file:
        file.readline()  # skip header
        for _ in tqdm(range(number_of_lines - 1)):
            line = list(file.readline().split(','))

            # Parse trip times
            try:
                start_time = datetime.strptime(line[1], "%m/%d/%Y %I:%M:%S %p")
                end_time = datetime.strptime(line[2], "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                continue  # skip invalid dates

            # Filter trips outside date range
            if not (start_date <= start_time <= end_date or start_date <= end_time <= end_date):
                continue

            # Skip trips with missing coordinates
            if line[10] == '' or line[11] == '' or line[13] == '' or line[14] == '':
                continue

            # Parse coordinates
            start_latitude = float(line[10])
            start_longitude = float(line[11])
            end_latitude = float(line[13])
            end_longitude = float(line[14])

            # Filter trips within geographic boundaries
            if lon_min <= start_longitude <= lon_max and lat_min <= start_latitude <= lat_max:
                trips.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'start_latitude': start_latitude,
                    'start_longitude': start_longitude,
                    'end_latitude': end_latitude,
                    'end_longitude': end_longitude
                })

    trips_df = pd.DataFrame(trips)
    return trips_df


def create_map(trips_df, start_date, end_date, shapefile_path):
    """
    Creates a trajectory map by plotting all trips on top of a city shapefile.

    Parameters
    ----------
    trips_df : pandas.DataFrame
        DataFrame containing trip start and end coordinates.
    start_date : datetime
        Start date for title and file naming.
    end_date : datetime
        End date for title and file naming.
    shapefile_path : str
        Path to the city shapefile to use as a base map.

    Returns
    -------
    None
        Saves a PNG file of the trajectory map.
    """
    city_gdf = gpd.read_file(shapefile_path)

    # Aggregate trips by unique start-end pairs
    route_counts = defaultdict(int)
    for _, trip in trips_df.iterrows():
        start_point = (trip['start_longitude'], trip['start_latitude'])
        end_point = (trip['end_longitude'], trip['end_latitude'])
        route = tuple(sorted([start_point, end_point]))  # order independent
        route_counts[route] += 1

    # Plot city map and trips
    fig, ax = plt.subplots(figsize=(12, 12))
    city_gdf.plot(ax=ax, color='lightgrey', edgecolor='black')

    # Plot each route, width proportional to trip count
    for route, count in route_counts.items():
        line = LineString(route)
        ax.plot(*line.xy, color='blue', linewidth=0.1 + count * 0.001, alpha=0.7)

    ax.set_ylim((41.66013746994182, 42.00962338))
    ax.set_xlim((-87.80370076, -87.5349023379022))
    ax.set_title('Trip Trajectory Map')
    plt.xticks([])
    plt.yticks([])

    map_filename = f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}_trajectory_map.png"
    plt.savefig(map_filename, bbox_inches='tight')


def create_trajectory_map(csv_file, start_day, end_day, shapefile_path):
    """
    Wrapper function to generate a trajectory map from a CSV file of trips.

    Parameters
    ----------
    csv_file : str
        Path to the CSV file containing trip data.
    start_day : str
        Start date in the format 'dd/mm/yyyy'.
    end_day : str
        End date in the format 'dd/mm/yyyy'.
    shapefile_path : str
        Path to the city shapefile to plot on.

    Returns
    -------
    None
        Reads trip data and generates a trajectory map PNG file.
    """
    start_date = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")
    trips_df = read_trips_file(csv_file, start_date=start_date, end_date=end_date)
    create_map(trips_df, start_date, end_date, shapefile_path)
