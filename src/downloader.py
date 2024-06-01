import requests
import zipfile
import os

def download_datasets():
    url_scooter = "https://data.cityofchicago.org/api/views/2i5w-ykuw/rows.csv?accessType=DOWNLOAD"
    response = requests.get(url_scooter)
    open('e_scooter_trips.csv', 'wb').write(response.content)

    url_map = "https://mapcruzin.com/download-shapefile/us/illinois_highway.zip"
    zip_filename = "illinois_highway.zip"
    response = requests.get(url_map)
    if response.status_code == 200:
        with open('illinois_highway.zip', 'wb') as file:
            file.write(response.content)
    else:
        print(f"Nie udało się pobrać pliku. Status kod: {response.status_code}")

    with zipfile.ZipFile('illinois_highway.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
    url_path = os.path.join(".", "Archive created by free jZip.url")
    zip_path = os.path.join(".", "illinois_highway.zip")
    readme_path = os.path.join(".", "readme.txt")
    if os.path.exists('.'):
        os.remove(url_path)
        os.remove(zip_path)
        os.remove(readme_path)

if __name__ == '__main__':
    download_datasets()
