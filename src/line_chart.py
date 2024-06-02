import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm
import sys
def read_trips_file(filename, start_date=None, end_date=None):
    margin = 0.1
    lon_min = -87.89370076 - margin
    lon_max = -87.5349023379022 + margin
    lat_min = 41.66013746994182 - margin
    lat_max = 42.00962338 + margin

    city_df = gpd.read_file('../results/01-04-2023_30-04-2023.shp')

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
    trips_df['weekday'] = trips_df['start_time'].dt.dayofweek
    trips_df['hour'] = trips_df['start_time'].dt.hour
    trips_df['is_weekend'] = trips_df['weekday'] >= 5

    weekday_trips = trips_df[~trips_df['is_weekend']].groupby('hour').size().reset_index(name='counts')
    weekend_trips = trips_df[trips_df['is_weekend']].groupby('hour').size().reset_index(name='counts')

    plt.figure(figsize=(12, 6))
    plt.plot(weekday_trips['hour'], weekday_trips['counts'], label='Dni powszednie', color='blue')
    plt.plot(weekend_trips['hour'], weekend_trips['counts'], label='Weekendy', color='orange')
    plt.xlabel('Godzina dnia')
    plt.ylabel('Liczba podróży')
    plt.title('Liczba przejazdów z podziałem na godziny w dni powszednie i weekendy')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}_trips_by_hour.png")

def create_line_chart(csv_file, start_day, end_day):
    start_date = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file(csv_file, start_date=start_date, end_date=end_date)