from datetime import datetime

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from shapely.wkt import loads
import networkx as nx
from geopy.distance import geodesic
import time


def closest_line(lines, point):
    # get distances
    distance_list = [line.distance(point) for line in lines]
    shortest_distance = min(distance_list)  # find the line closest to the point
    return lines[distance_list.index(shortest_distance)]  # return the distance to that line


def create_graph(df):
    G = nx.Graph()
    for idx, row in df.iterrows():
        line = row['geometry']
        nodes = list(line.coords)
        for i in range(len(nodes) - 1):
            G.add_edge(nodes[i], nodes[i + 1], weight=line.length)
    return G


def remove_elements_by_indexes(lst, indexes):
    indexes.sort(reverse=True)
    return [elem for i, elem in enumerate(lst) if i not in indexes]


def calculate_distance_from_path(path):
    if len(path) <= 1:
        return 0
    distances = [geodesic(path[i], path[i + 1]).meters for i in range(len(path) - 1)]
    linestring = LineString([(0, 0)] + [(sum(distances[:i + 1]), 0) for i in range(len(distances))])
    length = linestring.length
    return length


def read_trips_file(filename, row_limits=None, start_date=None, end_date=None):
    margin = 0.1
    city_df = gpd.read_file('illinois_highway.shp')
    city_df = filter_roads(city_df)
    city_df['visit_count'] = 0
    count = 0
    city_df = city_df.cx[-87.89370076 - margin:-87.5349023379022 + margin,
                         41.66013746994182 - margin:42.00962338 + margin]

    if row_limits is None:
        number_of_lines = sum(1 for _ in open(filename))
    else:
        number_of_lines = row_limits
    with open(filename, 'r') as file:
        file.readline()
        for _ in range(number_of_lines - 1):
            print(count)
            count+=1
            line = list(file.readline().split(','))
            start_time = datetime.strptime(line[1], "%m/%d/%Y %I:%M:%S %p")
            end_time = datetime.strptime(line[2], "%m/%d/%Y %I:%M:%S %p")
            if not start_date <= start_time <= end_date and not start_date <= end_time <= end_date:
                continue
            trip_distance = float(line[3])
            trip_duration = line[4]
            vendor = line[5]
            if line[10] == '' or line[11] == '' or line[13] == '' or line[14] == '':
                continue
            start_latitude = float(line[10])
            start_longitude = float(line[11])
            end_latitude = float(line[13])
            end_longitude = float(line[14])
            if start_latitude == end_latitude and start_longitude == end_longitude:
                continue
            bigger_latitude = start_latitude if start_latitude >= end_latitude else end_latitude
            smaller_latitude = start_latitude if start_latitude < end_latitude else end_latitude
            bigger_longitude = start_longitude if start_longitude >= end_longitude else end_longitude
            smaller_longitude = start_longitude if start_longitude < end_longitude else end_longitude
            df_roads_to_search = city_df.cx[smaller_longitude-margin:bigger_longitude+margin, smaller_latitude-margin:bigger_latitude+margin]
            df_roads_to_search = df_roads_to_search.reset_index(drop=True)
            start_point = Point(start_longitude, start_latitude)
            end_point = Point(end_longitude, end_latitude)
            start_point_closest_line = closest_line(df_roads_to_search['geometry'], start_point)
            end_point_closest_line = closest_line(df_roads_to_search['geometry'], end_point)
            start_point_closest_line_points_list = list(start_point_closest_line.coords)
            end_point_closest_line_points_list = list(end_point_closest_line.coords)
            G = create_graph(df_roads_to_search)
            shortest_path = nx.astar_path(G, start_point_closest_line_points_list[0], end_point_closest_line_points_list[0],
                                          heuristic=lambda u, v: 0)
            shortest_path_distance = calculate_distance_from_path(shortest_path)

            error = abs(shortest_path_distance-trip_distance)/trip_distance
            if error > 0.1:
                continue

            for index, row in df_roads_to_search.iterrows():
                at_least_one_point_intersects = False
                indexes_to_del = []
                if len(shortest_path)<=0:
                    break
                for i in range(len(shortest_path)):
                    if row['geometry'].intersects(Point(shortest_path[i])):
                        at_least_one_point_intersects = True
                        indexes_to_del.append(i)
                if at_least_one_point_intersects:
                    selected_path_index = city_df[city_df['geometry'] == row['geometry']].index[0]
                    city_df.loc[selected_path_index, 'visit_count'] = city_df.loc[selected_path_index, 'visit_count'] + 1
                shortest_path = remove_elements_by_indexes(shortest_path, indexes_to_del)
    # fig, ax = plt.subplots(1,1)
    # city_df.plot(ax=ax, zorder=1, column='visit_count', legend=True)
    # ax.set_xlim(-87.89370076 - margin, -87.5349023379022 + margin)
    # ax.set_ylim(41.66013746994182 - margin, 42.00962338 + margin)
    # ax.axis('off')
    # plt.show()
    city_df.to_file(f"{start_date}-{end_date}")


def filter_roads(df):
    return df[df['TYPE'].isin(
        ['living_street', 'service', 'track', 'crossing', 'cycleway', 'residential', 'pedestrian', 'footway',
         'sidewalk', 'footway', 'walkway', 'park road', 'cycleway;footway', 'cycleway; footway',
         'cycleway; footway; footway; footway', 'cycleway; footway; footway', 'footway; cycleway', 'service; cycleway',
         'secondary'])]


if __name__ == '__main__':
    start_date = datetime.strptime("01/02/2023 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime("28/02/2023 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file('E-Scooter_Trips_20240422.csv', start_date=start_date, end_date=end_date)
