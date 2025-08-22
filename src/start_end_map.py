from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd

def read_trips_file(filename, start_date=None, end_date=None):
    """
    Reads a CSV file containing trip data, aggregates start and end points,
    and plots them on a map using a shapefile of the city roads as a base.

    Parameters
    ----------
    filename : str
        Path to the CSV file containing trip data.
    start_date : datetime, optional
        Start date for filtering trips (inclusive). Default is None.
    end_date : datetime, optional
        End date for filtering trips (inclusive). Default is None.

    Returns
    -------
    None
        Saves a PNG file with aggregated trip points plotted on the city map.
    """
    # Define geographic boundaries (Chicago area) with a margin
    margin = 0.1
    lon_min = -87.89370076 - margin
    lon_max = -87.5349023379022 + margin
    lat_min = 41.66013746994182 - margin
    lat_max = 42.00962338 + margin

    # Load city roads shapefile
    city_df = gpd.read_file('../results/01-04-2023_30-04-2023.shp')

    points = []

    # Count total lines for progress bar
    number_of_lines = sum(1 for _ in open(filename))
    with open(filename, 'r') as file:
        file.readline()  # skip header
        for _ in tqdm(range(number_of_lines - 1)):
            line = list(file.readline().split(','))

            # Parse trip start and end times
            try:
                start_time = datetime.strptime(line[1], "%m/%d/%Y %I:%M:%S %p")
                end_time = datetime.strptime(line[2], "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                continue  # skip rows with invalid datetime

            # Filter trips outside the date range
            if not (start_date <= start_time <= end_date or start_date <= end_time <= end_date):
                continue

            # Skip rows with missing coordinates
            if line[10] == '' or line[11] == '' or line[13] == '' or line[14] == '':
                continue

            # Parse coordinates
            start_latitude = float(line[10])
            start_longitude = float(line[11])
            end_latitude = float(line[13])
            end_longitude = float(line[14])

            # Filter points within geographic boundaries
            if lon_min <= start_longitude <= lon_max and lat_min <= start_latitude <= lat_max:
                points.append((start_longitude, start_latitude))
            if lon_min <= end_longitude <= lon_max and lat_min <= end_latitude <= lat_max:
                points.append((end_longitude, end_latitude))

    # Aggregate points by location
    points_df = pd.DataFrame(points, columns=['longitude', 'latitude'])
    points_agg = points_df.groupby(['longitude', 'latitude']).size().reset_index(name='counts')

    # Create GeoDataFrame for plotting
    geometry = [Point(xy) for xy in zip(points_agg['longitude'], points_agg['latitude'])]
    gdf_points = gpd.GeoDataFrame(points_agg, geometry=geometry)

    # Plot city map and aggregated points
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_ylim((41.66013746994182, 42.00962338))
    ax.set_xlim((-87.80370076, -87.5349023379022))
    plt.xticks([])
    plt.yticks([])
    city_df.plot(ax=ax, zorder=1, edgecolor='k')
    gdf_points.plot(ax=ax, zorder=2, color='blue', markersize=gdf_points['counts'] * 0.05)

    plt.title('Aggregated Trip Points Map')
    plt.savefig(f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}_points.png",
                bbox_inches='tight')


def create_start_end_map(csv_file, start_day, end_day):
    """
    Wrapper function to convert date strings to datetime objects
    and generate an aggregated start/end point map.

    Parameters
    ----------
    csv_file : str
        Path to the CSV file containing trip data.
    start_day : str
        Start date in the format 'dd/mm/yyyy'.
    end_day : str
        End date in the format 'dd/mm/yyyy'.

    Returns
    -------
    None
        Calls read_trips_file to process trips and generate the map.
    """
    start_date = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file(csv_file, start_date=start_date, end_date=end_date)
