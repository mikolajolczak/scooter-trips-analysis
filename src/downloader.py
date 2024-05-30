import requests
import pandas as pd

# URL do pliku CSV
url = "https://data.cityofchicago.org/api/views/2i5w-ykuw/rows.csv?accessType=DOWNLOAD"

# Pobranie pliku CSV
response = requests.get(url)
open('e_scooter_trips.csv', 'wb').write(response.content)

# Wczytanie danych do Pandas DataFrame
df = pd.read_csv('e_scooter_trips.csv')

# Wyświetlenie pierwszych kilku wierszy DataFrame
print(df.head())

# Zapisanie DataFrame do pliku CSV (opcjonalne)
df.to_csv('e_scooter_trips_downloaded.csv', index=False)
