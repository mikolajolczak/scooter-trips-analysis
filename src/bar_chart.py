import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from typing import Optional

def read_trips_file(
    filename: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> None:
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
    """
    # Default dates
    if start_date is None:
        start_date = datetime.min
    if end_date is None:
        end_date = datetime.max

    # Geographic bounds (Chicago + margin)
    margin = 0.1
    lon_min = -87.89370076 - margin
    lon_max = -87.5349023379022 + margin
    lat_min = 41.66013746994182 - margin
    lat_max = 42.00962338 + margin

    # Read CSV
    try:
        trips_df: pd.DataFrame = pd.read_csv(filename, parse_dates=['start_time', 'end_time'])
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Filter by date range (keep trips fully within the range)
    trips_df = trips_df[
        (trips_df['start_time'] >= start_date) & (trips_df['end_time'] <= end_date)
    ]

    if trips_df.empty:
        print("No trips found in the specified date range.")
        return

    # Drop rows with missing coordinates
    trips_df = trips_df.dropna(subset=['start_latitude', 'start_longitude'])

    # Filter by geographic bounds
    trips_df = trips_df[
        trips_df['start_longitude'].between(lon_min, lon_max) &
        trips_df['start_latitude'].between(lat_min, lat_max)
    ]

    # Calculate trip duration in minutes and remove negative durations
    trips_df['duration'] = (trips_df['end_time'] - trips_df['start_time']).dt.total_seconds() / 60
    trips_df = trips_df[trips_df['duration'] >= 0]

    # Flag weekends
    trips_df['weekday'] = trips_df['start_time'].dt.weekday
    trips_df['is_weekend'] = trips_df['weekday'] >= 5

    # Calculate average duration for weekdays vs weekends
    avg_duration: pd.DataFrame = trips_df.groupby('is_weekend')['duration'].mean().reset_index()
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


def create_bar_chart(
    csv_file: str,
    start_day: str,
    end_day: str
) -> None:
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
    """
    start_date: datetime = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date: datetime = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file(csv_file, start_date=start_date, end_date=end_date)
