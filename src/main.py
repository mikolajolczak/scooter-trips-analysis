from datetime import datetime

import geopandas as gpd
from shapely.geometry import Point, LineString
import networkx as nx
from geopy.distance import geodesic
from tqdm import tqdm
import os
import downloader
import sys
from start_end_map import create_start_end_map
from trajectory import create_trajectory_map
from heatmap_creator import create_heat_map
from line_chart import create_line_chart
from bar_chart import create_bar_chart
def closest_line(lines, point):
    # Oblicza odległości między danym punktem a każdą linią z listy 'lines'
    distance_list = [line.distance(point) for line in lines]
    # Znajduje najkrótszą odległość
    shortest_distance = min(distance_list)
    # Zwraca linię o najkrótszej odległości do punktu
    return lines[distance_list.index(shortest_distance)]


def create_graph(df):
    # Tworzy graf (sieć) z danych geograficznych
    G = nx.Graph()
    for idx, row in df.iterrows():
        line = row['geometry']
        nodes = list(line.coords)
        # Dodaje krawędzie do grafu dla każdego odcinka linii
        for i in range(len(nodes) - 1):
            G.add_edge(nodes[i], nodes[i + 1], weight=line.length, line=line, line_index=idx)
    return G


def get_shortest_path_lines(df, start_point, end_point, G):
    # Znajduje najkrótszą ścieżkę w grafie G od start_point do end_point
    shortest_path = nx.astar_path(G, start_point, end_point, heuristic=lambda u, v: 0)

    # Zamienia punkty na linie
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
    # Usuwa elementy z listy lst na podstawie podanych indeksów
    indexes.sort(reverse=True)
    return [elem for i, elem in enumerate(lst) if i not in indexes]


def calculate_distance_from_path(path):
    # Oblicza odległość geodezyjną dla ścieżki z punktów
    if len(path) <= 1:
        return 0
    distances = [geodesic(path[i], path[i + 1]).meters for i in range(len(path) - 1)]
    linestring = LineString([(0, 0)] + [(sum(distances[:i + 1]), 0) for i in range(len(distances))])
    length = linestring.length
    return length


def read_trips_file(filename, row_limits=None, start_date=None, end_date=None):
    # Sprawdza, czy wymagane pliki istnieją, jeśli nie, pobiera je
    if not (os.path.exists('illinois_highway.shp') and os.path.exists('e_scooter_trips.csv') and
            os.path.exists('illinois_highway.dbf') and os.path.exists('illinois_highway.prj') and
            os.path.exists('illinois_highway.shx')):
        print("Nie znaleziono zbiorów danych. Rozpoczynam pobieranie...")
        downloader.download_datasets()

    margin = 0.1
    city_df = gpd.read_file('illinois_highway.shp')
    city_df = filter_roads(city_df)
    city_df['count_work'] = 0
    city_df['count_free'] = 0
    city_df['count_lyft'] = 0
    city_df['count_lime'] = 0
    city_df['count_link'] = 0
    city_df = city_df.cx[-87.89370076 - margin:-87.5349023379022 + margin,
                         41.66013746994182 - margin:42.00962338 + margin]
    city_df = city_df.reset_index(drop=True)
    G = create_graph(city_df)

    if row_limits is None:
        number_of_lines = sum(1 for _ in open(filename))
    else:
        number_of_lines = row_limits

    with open(filename, 'r') as file:
        file.readline()  # Pomija nagłówek
        for _ in tqdm(range(number_of_lines - 1)):
            line = list(file.readline().split(','))
            try:
                start_time = datetime.strptime(line[1], "%m/%d/%Y %I:%M:%S %p")
                end_time = datetime.strptime(line[2], "%m/%d/%Y %I:%M:%S %p")
            except:
                continue

            # Filtruje przejazdy poza zakresem dat
            if not start_date <= start_time <= end_date and not start_date <= end_time <= end_date:
                continue

            trip_distance = float(line[3])
            trip_duration = line[4]
            vendor = line[5]

            # Pomija przejazdy z brakującymi danymi lokalizacji
            if line[10] == '' or line[11] == '' or line[13] == '' or line[14] == '':
                continue

            start_latitude = float(line[10])
            start_longitude = float(line[11])
            end_latitude = float(line[13])
            end_longitude = float(line[14])

            # Pomija przejazdy, gdzie punkt startu i końca jest taki sam
            if start_latitude == end_latitude and start_longitude == end_longitude:
                continue

            start_point = Point(start_longitude, start_latitude)
            end_point = Point(end_longitude, end_latitude)

            # Znajduje najbliższe linie do punktów startu i końca
            start_point_closest_line = closest_line(city_df['geometry'], start_point)
            end_point_closest_line = closest_line(city_df['geometry'], end_point)

            start_point_closest_line_points_list = list(start_point_closest_line.coords)
            end_point_closest_line_points_list = list(end_point_closest_line.coords)

            # Znajduje najkrótszą ścieżkę między punktami startu i końca
            shortest_path, line_indices = get_shortest_path_lines(city_df,
                                                                  start_point_closest_line_points_list[0],
                                                                  end_point_closest_line_points_list[0], G)
            shortest_path_distance = calculate_distance_from_path(shortest_path)

            # Oblicza błąd odległości i pomija, jeśli jest większy niż 10%
            error = abs(shortest_path_distance - trip_distance) / trip_distance
            if error > 0.1:
                continue

            # Zwiększa liczniki dla odpowiednich linii na podstawie dnia tygodnia i dostawcy
            if start_time.weekday() < 5:
                city_df.loc[line_indices, 'count_work'] += 1
            else:
                city_df.loc[line_indices, 'count_free'] += 1

            if vendor == "Lime":
                city_df.loc[line_indices, 'count_lime'] += 1
            if vendor == "Lyft":
                city_df.loc[line_indices, 'count_lyft'] += 1
            if vendor == "Link":
                city_df.loc[line_indices, 'count_link'] += 1

    # Zapisuje zaktualizowany zbiór danych do pliku
    city_df.to_file(f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}.shp")


def filter_roads(df):
    # Filtruje drogi, pozostawiając tylko określone typy
    return df[df['TYPE'].isin(
        ['living_street', 'service', 'track', 'crossing', 'cycleway', 'residential', 'pedestrian', 'footway',
         'sidewalk', 'footway', 'walkway', 'park road', 'cycleway;footway', 'cycleway; footway',
         'cycleway; footway; footway; footway', 'cycleway; footway; footway', 'footway; cycleway', 'service; cycleway',
         'secondary'])]


if __name__ == '__main__':
    csv_file = sys.argv[1]
    start_day = sys.argv[2]
    end_day = sys.argv[3]
    result_shapefile_path = f"{start_day.replace('/','-')}_{start_day.replace('/','-')}.shp"
    start_date = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file(csv_file, start_date=start_date, end_date=end_date)
    create_heat_map(result_shapefile_path)
    create_bar_chart(csv_file,start_day,end_day)
    create_line_chart(csv_file, start_day, end_day)
    create_start_end_map(csv_file, start_day, end_day)
    create_trajectory_map(csv_file, start_day, end_day, result_shapefile_path)
