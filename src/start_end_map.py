from datetime import datetime

import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
from geopy.distance import geodesic
from tqdm import tqdm
import os
import downloader
import matplotlib.pyplot as plt
import pandas as pd


def read_trips_file(filename, start_date=None, end_date=None):
    margin = 0.1
    lon_min = -87.89370076 - margin
    lon_max = -87.5349023379022 + margin
    lat_min = 41.66013746994182 - margin
    lat_max = 42.00962338 + margin

    city_df = gpd.read_file('../results/01-04-2023_30-04-2023.shp')

    points = []

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
                points.append((start_longitude, start_latitude))
            if lon_min <= end_longitude <= lon_max and lat_min <= end_latitude <= lat_max:
                points.append((end_longitude, end_latitude))

    points_df = pd.DataFrame(points, columns=['longitude', 'latitude'])
    points_agg = points_df.groupby(['longitude', 'latitude']).size().reset_index(name='counts')
    geometry = [Point(xy) for xy in zip(points_agg['longitude'], points_agg['latitude'])]
    gdf_points = gpd.GeoDataFrame(points_agg, geometry=geometry)

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_ylim(( 41.66013746994182, 42.00962338))
    ax.set_xlim((-87.80370076, -87.5349023379022))
    plt.xticks([])
    plt.yticks([])
    city_df.plot(ax=ax, zorder=1, edgecolor='k')
    gdf_points.plot(ax=ax, zorder=2, color='blue', markersize=gdf_points['counts']*0.3)

    plt.title('Mapa zagregowanych punktów podróży')
    plt.savefig(f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}_points.png", bbox_inches='tight')

if __name__ == '__main__':
    start_date = datetime.strptime("01/04/2023 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime("07/04/2023 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file('e_scooter_trips.csv', start_date=start_date, end_date=end_date)
