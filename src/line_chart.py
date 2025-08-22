import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Optional


def read_trips_file(
        csv_file: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> None:
    """
    Reads a CSV file containing trip data, filters trips by date and geographic boundaries,
    aggregates trips by hour for weekdays and weekends, and generates a line chart.

    Parameters
    ----------
    csv_file : str
        Path to the CSV file containing trip data.
    start_date : datetime, optional
        Start of the date range for filtering trips (default is None).
    end_date : datetime, optional
        End of the date range for filtering trips (default is None).

    Returns
    -------
    None
        Saves a line chart of trips by hour for weekdays and weekends as a PNG file.
    """
    # Define geographic boundaries (Chicago)
    margin = 0.1
    lon_min = -87.89370076 - margin
    lon_max = -87.5349023379022 + margin
    lat_min = 41.66013746994182 - margin
    lat_max = 42.00962338 + margin

    # Load CSV using pandas, parse datetime columns
    df: pd.DataFrame = pd.read_csv(
        csv_file,
        usecols=[1, 2, 10, 11, 13, 14],  # Only read necessary columns
        parse_dates=[1, 2],
        names=['start_time', 'end_time', 'start_lat', 'start_lon', 'end_lat', 'end_lon'],
        header=0
    )

    # Filter rows with missing coordinates
    df = df.dropna(subset=['start_lat', 'start_lon', 'end_lat', 'end_lon'])

    # Filter by geographic boundaries
    df = df[
        (df['start_lon'].between(lon_min, lon_max)) &
        (df['start_lat'].between(lat_min, lat_max))
        ]

    # Filter by date range if provided
    if start_date:
        df = df[df['start_time'] >= start_date]
    if end_date:
        df = df[df['end_time'] <= end_date]

    # Add weekday, hour, and weekend flags
    df['weekday'] = df['start_time'].dt.dayofweek
    df['hour'] = df['start_time'].dt.hour
    df['is_weekend'] = df['weekday'] >= 5

    # Aggregate trips by hour for weekdays and weekends
    weekday_trips: pd.Series = df[~df['is_weekend']].groupby('hour').size()
    weekend_trips: pd.Series = df[df['is_weekend']].groupby('hour').size()

    # Plot line chart
    plt.figure(figsize=(12, 6))
    plt.plot(weekday_trips.index, weekday_trips.values, label='Weekdays', color='blue')
    plt.plot(weekend_trips.index, weekend_trips.values, label='Weekends', color='orange')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Trips')
    plt.title('Number of Trips by Hour for Weekdays and Weekends')
    plt.legend()
    plt.grid(True)

    # Handle case when start_date or end_date is None
    filename = "trips_by_hour.png"
    if start_date and end_date:
        filename = f"{start_date.strftime('%d-%m-%Y')}_{end_date.strftime('%d-%m-%Y')}_trips_by_hour.png"
    plt.savefig(filename)


def create_line_chart(
        csv_file: str,
        start_day: str,
        end_day: str
) -> None:
    """
    Wrapper function to convert date strings to datetime objects and generate
    a line chart of trips by hour.

    Parameters
    ----------
    csv_file : str
        Path to the CSV file containing trip data.
    start_day : str
        Start date in the format 'dd/mm/yyyy'.
    end_day : str
        End date in the format 'dd/mm/yyyy'.

    Returns
    -------
    None
    """
    start_date: datetime = datetime.strptime(f"{start_day} 00:00:00", "%d/%m/%Y %H:%M:%S")
    end_date: datetime = datetime.strptime(f"{end_day} 23:59:59", "%d/%m/%Y %H:%M:%S")
    read_trips_file(csv_file, start_date=start_date, end_date=end_date)
