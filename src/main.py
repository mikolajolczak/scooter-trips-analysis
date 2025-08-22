from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
from geopy.distance import geodesic
from tqdm import tqdm
import os
import sys

import downloader
from start_end_map import create_start_end_map
from trajectory import create_trajectory_map
from heatmap_creator import create_heat_map
from line_chart import create_line_chart
from bar_chart import create_bar_chart


def closest_line(lines, point):
    """
    Finds the closest line from a list of lines to a given point.

    Parameters
    ----------
    lines : list of shapely LineString
        List of line geometries.
    point : shapely Point
        The point to find the closest line to.

    Returns
    -------
    shapely LineString
        The line closest to the given point.
    """
    distances = [line.distance(point) for line in lines]
    shortest_distance = min(distances)
    return lines[distances.index(shortest_distance)]


def create_graph(df):
    """
    Creates a NetworkX graph from a GeoDataFrame of line geometries.

    Parameters
    ----------
    df : geopandas.GeoDataFrame
        GeoDataFrame containing line geometries in 'geometry' column.

    Returns
    -------
    networkx.Graph
        A graph where nodes are coordinates and edges represent line segments.
    """
    g = nx.Graph()
    for idx, row in df.iterrows():
        line = row['geometry']
        nodes = list(line.coords)
        for i in range(len(nodes) - 1):
            g.add_edge(nodes[i], nodes[i + 1], weight=line.length, line=line, line_index=idx)
    return g


def get_shortest_path_lines(start_point, end_point, g):
    """
    Finds the shortest path in a graph between two points and returns the corresponding lines.

    Parameters
    ----------
    start_point : tuple
        Coordinates of the start point.
    end_point : tuple
        Coordinates of the end point.
    g : networkx.Graph
        Graph created from line geometries.

    Returns
    -------
    shortest_path : list of tuples
        Sequence of coordinates in the shortest path.
    line_indices : list of int
        Indices of the lines in the GeoDataFrame that correspond to the path.
    """
    shortest_path = nx.astar_path(g, start_point, end_point, heuristic=lambda u, v: 0)
    path_lines = []
    line_indices = []

    for i in range(len(shortest_path) - 1):
        edge_data = g.get_edge_data(shortest_path[i], shortest_path[i + 1])
        if 'line_index' in edge_data:
            path_lines.append(edge_data['line'])
            line_indices.append(edge_data['line_index'])
        else:
            print(f"Missing 'line_index' for edge between {shortest_path[i]} and {shortest_path[i + 1]}")

    return shortest_path, list(set(line_indices))


def remove_elements_by_indexes(lst, indexes):
    """
    Removes elements from a list by their indexes.

    Parameters
    ----------
    lst : list
        Original list.
    indexes : list of int
        Indexes of elements to remove.

    Returns
    -------
    list
        New list with specified elements removed.
    """
    indexes.sort(reverse=True)
    return [elem for i, elem in enumerate(lst) if i not in indexes]


def calculate_distance_from_path(path):
    """
    Calculates the geodesic distance of a path defined by a list of coordinates.

    Parameters
    ----------
    path : list of tuples
        List of (longitude, latitude) coordinates.

    Returns
    -------
    float
        Total path distance in meters.
    """
    if len(path) <= 1:
        return 0
    distances = [geodesic(path[i], path[i + 1]).meters for i in range(len(path) - 1)]
    # Create a LineString representing cumulative distance (optional)
    linestring = LineString([(0, 0)] + [(sum(distances[:i + 1]), 0) for i in range(len(distances))])
    return linestring.length


def filter_roads(df):
    """
    Filters a GeoDataFrame of roads, keeping only specific road types.

    Parameters
    ----------
    df : geopandas.GeoDataFrame
        Original road GeoDataFrame.

    Returns
    -------
    geopandas.GeoDataFrame
        Filtered GeoDataFrame containing only selected road types.
    """
    valid_types = [
        'living_street', 'service', 'track', 'crossing', 'cycleway', 'residential',
        'pedestrian', 'footway', 'sidewalk', 'walkway', 'park road', 'cycleway;footway',
        'cycleway; footway', 'cycleway; footway; footway; footway', 'cycleway; footway; footway',
        'footway; cycleway', 'service; cycleway', 'secondary'
    ]
    return df[df['TYPE'].isin(valid_types)]


def read_trips_file(filename, row_limits=None, start=None, end=None):
    """
    Reads trip data, filters by date and location, maps trips to road network, 
    counts trips by type and vendor, and saves results as a shapefile.

    Parameters
    ----------
    filename : str
        Path to the CSV file containing trip data.
    row_limits : int, optional
        Maximum number of rows to process from the CSV.
    start : datetime, optional
        Start date for filtering trips.
    end : datetime, optional
        End date for filtering trips.

    Returns
    -------
    None
        Saves the updated GeoDataFrame with trip counts as a shapefile.
    """
    # Download datasets if missing
    required_files = ['illinois_highway.shp', 'illinois_highway.dbf', 'illinois_highway.prj',
                      'illinois_highway.shx', 'e_scooter_trips.csv']
    if not all(os.path.exists(f) for f in required_files):
        print("Datasets not found. Downloading...")
        downloader.download_datasets()

    # Load and filter roads
    margin = 0.1
    city_df = gpd.read_file('illinois_highway.shp')
    city_df = filter_roads(city_df)
    city_df[['count_work', 'count_free', 'count_lyft', 'count_lime', 'count_link']] = 0
    city_df = city_df.cx[-87.89370076 - margin:-87.5349023379022 + margin,
                         41.66013746994182 - margin:42.00962338 + margin].reset_index(drop=True)

    g = create_graph(city_df)

    # Determine number of lines to process
    number_of_lines = row_limits or sum(1 for _ in open(filename))

    with open(filename, 'r') as file:
        file.readline()  # skip header
        for _ in tqdm(range(number_of_lines - 1)):
            line = list(file.readline().split(','))

            # Parse times and skip invalid
            try:
                start_time = datetime.strptime(line[1], "%m/%d/%Y %I:%M:%S %p")
                end_time = datetime.strptime(line[2], "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                continue

            # Filter trips outside date range
            if not start <= start_time <= end and not start <= end_time <= end:
                continue

            trip_distance = float(line[3])
            vendor = line[5]

            # Skip trips with missing coordinates
            if line[10] == '' or line[11] == '' or line[13] == '' or line[14] == '':
                continue

            start_lat, start_lon = float(line[10]), float(line[11])
            end_lat, end_lon = float(line[13]), float(line[14])

            if start_lat == end_lat and start_lon == end_lon:
                continue

            start_point = Point(start_lon, start_lat)
            end_point = Point(end_lon, end_lat)

            start_line = closest_line(city_df['geometry'], start_point)
            end_line = closest_line(city_df['geometry'], end_point)

            start_points = list(start_line.coords)
            end_points = list(end_line.coords)

            shortest_path, line_indices = get_shortest_path_lines(start_points[0], end_points[0], g)
            shortest_path_distance = calculate_distance_from_path(shortest_path)

            # Skip if distance error > 10%
            if abs(shortest_path_distance - trip_distance) / trip_distance > 0.1:
                continue

            # Update counts by weekday/weekend
            if start_time.weekday() < 5:
                city_df.loc[line_indices, 'count_work'] += 1
            else:
                city_df.loc[line_indices, 'count_free'] += 1

            # Update counts by vendor
            if vendor == "Lime":
                city_df.loc[line_indices, 'count_lime'] += 1
            if vendor == "Lyft":
                city_df.loc[line_indices, 'count_lyft'] += 1
            if vendor == "Link":
                city_df.loc[line_indices, 'count_link'] += 1

    # Save updated GeoDataFrame
    city_df.to_file(f"{start.strftime('%d-%m-%Y')}_{end.strftime('%d-%m-%Y')}.shp")


if __name__ == '__main__':
    csv_file = sys.argv[1]
    start_day = sys.argv[2]
    end_day = sys.argv[3]

    result_shapefile_path = f"{start_day.replace('/', '-')}_{end_day.replace('/', '-')}.shp"
    start_date = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")

    # Process trips and generate shapefile
    read_trips_file(csv_file, start=start_date, end=end_date)

    # Generate maps and charts
    create_heat_map(result_shapefile_path)
    create_bar_chart(csv_file, start_day, end_day)
    create_line_chart(csv_file, start_day, end_day)
    create_start_end_map(csv_file, start_day, end_day)
    create_trajectory_map(csv_file, start_day, end_day, result_shapefile_path)
