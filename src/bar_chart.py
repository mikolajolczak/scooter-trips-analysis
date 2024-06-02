import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from tqdm import tqdm

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
                    'duration': (end_time - start_time).total_seconds() / 60,
                    'weekday': start_time.weekday(),
                }
                trips.append(trip)

    trips_df = pd.DataFrame(trips)
    trips_df['is_weekend'] = trips_df['weekday'] >= 5

    avg_duration = trips_df.groupby('is_weekend')['duration'].mean().reset_index()
    avg_duration['is_weekend'] = avg_duration['is_weekend'].map({True: 'Weekend/Dni Wolne', False: 'Dni robocze'})

    plt.figure(figsize=(10, 6))
    sns.barplot(x='is_weekend', y='duration', data=avg_duration, palette='viridis')
    plt.xlabel('Rodzaj dnia')
    plt.ylabel('Średni czas trwania przejazdów (minuty)')
    plt.title('Wykres czasu trwania przejazdów')
    plt.savefig(f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}_avg_ride_duration.png")

if __name__ == '__main__':
    start_date = datetime.strptime("01/04/2023 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime("07/04/2023 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file('e_scooter_trips.csv', start_date=start_date, end_date=end_date)