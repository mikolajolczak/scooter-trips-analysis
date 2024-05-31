from datetime import datetime

import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
from geopy.distance import geodesic
from tqdm import tqdm

def closest_line(lines, point):
    # get distances
    distance_list = [line.distance(point) for line in lines]
    shortest_distance = min(distance_list)
    return lines[distance_list.index(shortest_distance)]


def create_graph(df):
    G = nx.Graph()
    for idx, row in df.iterrows():
        line = row['geometry']
        nodes = list(line.coords)
        for i in range(len(nodes) - 1):
            G.add_edge(nodes[i], nodes[i + 1], weight=line.length, line=line, line_index=idx)
    return G


def get_shortest_path_lines(df, start_point, end_point, G):
    shortest_path = nx.astar_path(G, start_point, end_point, heuristic=lambda u, v: 0)

    # Zamiana punktów na linie
    path_lines = []
    line_indices = []
    for i in range(len(shortest_path) - 1):
        edge_data = G.get_edge_data(shortest_path[i], shortest_path[i + 1])
        if 'line_index' in edge_data:
            line = edge_data['line']
            line_index = edge_data['line_index']
            path_lines.append(line)
            line_indices.append(line_index)
        else:
            print(f"Brak 'line_index' dla krawędzi pomiędzy {shortest_path[i]} i {shortest_path[i + 1]}")

    return shortest_path, list(set(line_indices))


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
    city_df['count_work'] = 0
    city_df['count_free'] = 0
    city_df = city_df.cx[-87.89370076 - margin:-87.5349023379022 + margin,
              41.66013746994182 - margin:42.00962338 + margin]
    city_df = city_df.reset_index(drop=True)
    G = create_graph(city_df)
    if row_limits is None:
        number_of_lines = sum(1 for _ in open(filename))
    else:
        number_of_lines = row_limits
    with open(filename, 'r') as file:
        file.readline()
        for _ in tqdm(range(number_of_lines - 1)):
            line = list(file.readline().split(','))
            try:
                start_time = datetime.strptime(line[1], "%m/%d/%Y %I:%M:%S %p")
                end_time = datetime.strptime(line[2], "%m/%d/%Y %I:%M:%S %p")
            except:
                continue
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
            start_point = Point(start_longitude, start_latitude)
            end_point = Point(end_longitude, end_latitude)
            start_point_closest_line = closest_line(city_df['geometry'], start_point)
            end_point_closest_line = closest_line(city_df['geometry'], end_point)
            start_point_closest_line_points_list = list(start_point_closest_line.coords)
            end_point_closest_line_points_list = list(end_point_closest_line.coords)
            shortest_path, line_indices = get_shortest_path_lines(city_df,
                                                                  start_point_closest_line_points_list[0],
                                                                  end_point_closest_line_points_list[0], G)
            shortest_path_distance = calculate_distance_from_path(shortest_path)
            error = abs(shortest_path_distance - trip_distance) / trip_distance
            if error > 0.1:
                continue
            if start_time.weekday() < 5:
                city_df.loc[line_indices, 'count_work'] += 1
            else:
                city_df.loc[line_indices, 'count_free'] += 1

    city_df.to_file(f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}.shp")


def filter_roads(df):
    return df[df['TYPE'].isin(
        ['living_street', 'service', 'track', 'crossing', 'cycleway', 'residential', 'pedestrian', 'footway',
         'sidewalk', 'footway', 'walkway', 'park road', 'cycleway;footway', 'cycleway; footway',
         'cycleway; footway; footway; footway', 'cycleway; footway; footway', 'footway; cycleway', 'service; cycleway',
         'secondary'])]


if __name__ == '__main__':
    start_date = datetime.strptime("10/05/2022 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime("16/05/2022 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file('e_scooter_trips.csv', start_date=start_date, end_date=end_date)
