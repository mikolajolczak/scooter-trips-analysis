import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from datetime import datetime
from tqdm import tqdm
from collections import defaultdict

def read_trips_file(filename, start_date=None, end_date=None):
    margin = 0.1
    lon_min = -87.89370076 - margin
    lon_max = -87.5349023379022 + margin
    lat_min = 41.66013746994182 - margin
    lat_max = 42.00962338 + margin

    trips = []

    number_of_lines = sum(1 for _ in open(filename))
    with open(filename, 'r') as file:
        file.readline()
        for _ in tqdm(range(number_of_lines - 1)):
            line = list(file.readline().split(','))
            try:
                start_time = datetime.strptime(line[1], "%m/%d/%Y %I:%M:%S %p")
                end_time = datetime.strptime(line[2], "%m/%d/%Y %I:%M:%S %p")
            except:
                continue
            if not (start_date <= start_time <= end_date or start_date <= end_time <= end_date):
                continue
            if line[10] == '' or line[11] == '' or line[13] == '' or line[14] == '':
                continue
            start_latitude = float(line[10])
            start_longitude = float(line[11])
            end_latitude = float(line[13])
            end_longitude = float(line[14])

            if lon_min <= start_longitude <= lon_max and lat_min <= start_latitude <= lat_max:
                trip = {
                    'start_time': start_time,
                    'end_time': end_time,
                    'start_latitude': start_latitude,
                    'start_longitude': start_longitude,
                    'end_latitude': end_latitude,
                    'end_longitude': end_longitude
                }
                trips.append(trip)

    trips_df = pd.DataFrame(trips)
    return trips_df

def create_map(trips_df, start_date, end_date, shapefile_path):
    city_gdf = gpd.read_file(shapefile_path)

    route_counts = defaultdict(int)
    for _, trip in trips_df.iterrows():
        start_point = (trip['start_longitude'], trip['start_latitude'])
        end_point = (trip['end_longitude'], trip['end_latitude'])
        route = tuple(sorted([start_point, end_point]))
        route_counts[route] += 1

    fig, ax = plt.subplots(figsize=(12, 12))
    city_gdf.plot(ax=ax, color='lightgrey', edgecolor='black')
    for route, count in route_counts.items():
        line = LineString(route)
        ax.plot(*line.xy, color='blue', linewidth=0.1 + count * 0.001, alpha=0.7)

    ax.set_ylim((41.66013746994182, 42.00962338))
    ax.set_xlim((-87.80370076, -87.5349023379022))
    ax.set_title('Mapa trajektorii przejazdów')
    plt.xticks([])
    plt.yticks([])
    map_filename = f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}_trajectory_map.png"
    plt.savefig(map_filename, bbox_inches='tight')

def create_trajectory_map(csv_file, start_day, end_day, shapefile_path):
    start_date = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")
    trips_df = read_trips_file(csv_file, start_date=start_date, end_date=end_date)
    create_map(trips_df, start_date, end_date, shapefile_path)