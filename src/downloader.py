import requests
import zipfile
import os


def download_datasets():
    """
    Downloads datasets needed for analysis:
    1. E-scooter trip CSV data from City of Chicago.
    2. Illinois highway shapefile as a ZIP archive.

    The function saves the CSV as 'e_scooter_trips.csv' and extracts the shapefile
    from 'illinois_highway.zip'. After extraction, it attempts to remove unnecessary
    files including the ZIP and readme files.

    Returns
    -------
    None
    """
    # URL for e-scooter trip dataset (CSV)
    url_scooter = "https://data.cityofchicago.org/api/views/2i5w-ykuw/rows.csv?accessType=DOWNLOAD"

    # Download the CSV and save it locally
    response = requests.get(url_scooter)
    open('e_scooter_trips.csv', 'wb').write(response.content)

    # URL for Illinois highway shapefile (ZIP)
    url_map = "https://mapcruzin.com/download-shapefile/us/illinois_highway.zip"
    zip_filename = "illinois_highway.zip"

    # Download the ZIP file
    response = requests.get(url_map)
    if response.status_code == 200:
        with open(zip_filename, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

    # Extract the ZIP file contents
    with zipfile.ZipFile('illinois_highway.zip', 'r') as zip_ref:
        zip_ref.extractall('.')

    # Attempt to clean up unnecessary files
    url_path = os.path.join(".", "Archive created by free jZip.url")
    zip_path = os.path.join(".", "illinois_highway.zip")
    readme_path = os.path.join(".", "readme.txt")

    # Remove the files if they exist
    for file_path in [url_path, zip_path, readme_path]:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == '__main__':
    download_datasets()
