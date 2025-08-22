import requests
import zipfile
import os
from tqdm import tqdm

def download_file(url: str, filename: str) -> None:
    """Download a file from a given URL with a progress bar.

    Args:
        url (str): The URL to download the file from.
        filename (str): The local path where the file will be saved.

    Returns:
        None
    """
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024

    with open(filename, 'wb') as file, tqdm(
        total=total_size, unit='iB', unit_scale=True, desc=filename
    ) as bar:
        for data in response.iter_content(block_size):
            file.write(data)
            bar.update(len(data))


def download_datasets() -> None:
    """Download e-scooter trip CSV and Illinois highway shapefile.

    The function performs the following steps:
        1. Downloads the e-scooter trip CSV from the City of Chicago.
        2. Downloads the Illinois highway shapefile ZIP archive.
        3. Extracts the contents of the ZIP file.
        4. Cleans up unnecessary files (ZIP and readme files).

    The CSV is saved as 'e_scooter_trips.csv'.
    The shapefile is extracted to the current directory.

    Returns:
        None
    """
    url_scooter = "https://data.cityofchicago.org/api/views/2i5w-ykuw/rows.csv?accessType=DOWNLOAD"
    url_map = "https://mapcruzin.com/download-shapefile/us/illinois_highway.zip"

    # Download files
    download_file(url_scooter, "e_scooter_trips.csv")
    download_file(url_map, "illinois_highway.zip")

    # Extract ZIP file
    with zipfile.ZipFile('illinois_highway.zip', 'r') as zip_ref:
        zip_ref.extractall('.')

    # Clean up unnecessary files
    files_to_remove = [
        os.path.join(".", "Archive created by free jZip.url"),
        os.path.join(".", "illinois_highway.zip"),
        os.path.join(".", "readme.txt"),
    ]

    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == '__main__':
    download_datasets()
