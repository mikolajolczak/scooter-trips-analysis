import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from tqdm import tqdm
import os

def read_trips_file(filename, start_date=None, end_date=None):
    """
    Reads a CSV file containing trip data, filters trips by date and location,
    calculates average trip duration for weekdays and weekends, and generates a bar plot.

    Parameters
    ----------
    filename : str
        Path to the CSV file containing trip data.
    start_date : datetime, optional
        Start of the date range for filtering trips (default is earliest possible date).
    end_date : datetime, optional
        End of the date range for filtering trips (default is latest possible date).

    Returns
    -------
    None
        Saves a bar plot of average trip duration in the 'plots' folder.
        Prints a message if no trips are found in the specified date range.
    """
    if start_date is None:
        start_date = datetime.min
    if end_date is None:
        end_date = datetime.max

    # Geographic bounds for filtering trips (Chicago + margin)
    margin = 0.1
    lon_min = -87.89370076 - margin
    lon_max = -87.5349023379022 + margin
    lat_min = 41.66013746994182 - margin
    lat_max = 42.00962338 + margin

    trips = []

    with open(filename, 'r') as file:
        file.readline()  # skip header
        for line in tqdm(file):
            fields = line.strip().split(',')

            # Parse start and end times, skip rows with invalid format
            try:
                start_time = datetime.strptime(fields[1], "%m/%d/%Y %I:%M:%S %p")
                end_time = datetime.strptime(fields[2], "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                continue

            # Filter trips outside the specified date range
            if not (start_date <= start_time <= end_date or start_date <= end_time <= end_date):
                continue

            # Skip rows with missing coordinates
            if not all(fields[i] for i in [10, 11, 13, 14]):
                continue

            start_latitude = float(fields[10])
            start_longitude = float(fields[11])

            # Filter trips outside the geographic bounds
            if not (lon_min <= start_longitude <= lon_max and lat_min <= start_latitude <= lat_max):
                continue

            # Append trip info
            trip = {
                'start_time': start_time,
                'end_time': end_time,
                'duration': (end_time - start_time).total_seconds() / 60,  # duration in minutes
                'weekday': start_time.weekday(),  # Monday=0, Sunday=6
            }
            trips.append(trip)

    # Convert to DataFrame
    trips_df = pd.DataFrame(trips)

    if trips_df.empty:
        print("No trips found in the specified date range.")
        return

    # Flag weekends
    trips_df['is_weekend'] = trips_df['weekday'] >= 5

    # Calculate average duration for weekdays vs weekends
    avg_duration = trips_df.groupby('is_weekend')['duration'].mean().reset_index()
    avg_duration['is_weekend'] = avg_duration['is_weekend'].map({True: 'Weekend', False: 'Weekday'})

    # Ensure the "plots" folder exists
    os.makedirs("plots", exist_ok=True)

    # Plot average trip duration
    plt.figure(figsize=(10, 6))
    sns.barplot(x='is_weekend', y='duration', data=avg_duration, palette='viridis')
    plt.xlabel('Day Type')
    plt.ylabel('Average Trip Duration (minutes)')
    plt.title('Average Trip Duration')
    plt.savefig(f"plots/{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}_avg_ride_duration.png")
    plt.close()


def create_bar_chart(csv_file, start_day, end_day):
    """
    Wrapper function to convert date strings to datetime objects
    and generate the average trip duration bar chart.

    Parameters
    ----------
    csv_file : str
        Path to the CSV file containing trip data.
    start_day : str
        Start date in format 'dd/mm/yyyy'.
    end_day : str
        End date in format 'dd/mm/yyyy'.

    Returns
    -------
    None
        Calls read_trips_file to process the data and generate the plot.
    """
    # Convert date strings to datetime objects
    start_date = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")
    # Read trips and generate the chart
    read_trips_file(csv_file, start_date=start_date, end_date=end_date)
