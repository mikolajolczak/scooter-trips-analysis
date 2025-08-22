import geopandas as gpd
import matplotlib.pyplot as plt


def show_map(
    geodataframe: gpd.GeoDataFrame,
    column: str,
    title: str = "Map",
    is_cut: bool = False
) -> None:
    """
    Plots a GeoDataFrame as a choropleth map with variable line widths
    depending on the column values and saves it as a PNG file.

    Parameters
    ----------
    geodataframe : geopandas.GeoDataFrame
        The GeoDataFrame containing the spatial data to plot.
    column : str
        The column name to use for coloring and line width.
    title : str, optional
        The title of the map (default is "Map").
    is_cut : bool, optional
        If True, sets a smaller latitude range for a zoomed-in view
        (default is False).

    Returns
    -------
    None
        Saves the map as a PNG file in the current directory.
    """
    fig, ax = plt.subplots(1, 1, figsize=(30, 20))

    # Define line width based on column value
    def get_linewidth(value: float) -> float:
        return 2 if value > 0 else 0.5
    linewidths = geodataframe[column].apply(get_linewidth)

    # Plot the GeoDataFrame
    plot = geodataframe.plot(ax=ax, column=column, legend=True, cmap='plasma', linewidth=linewidths)

    # Set map limits: latitude range is adjusted if 'is_cut' is True
    ax.set_ylim((41.85013746994182 if is_cut else 41.66013746994182, 42.00962338))
    ax.set_xlim((-87.80370076, -87.5349023379022))

    # Set title and remove axis ticks
    ax.set_title(title, fontsize=30)
    plt.xticks([])
    plt.yticks([])

    # Customize colorbar label
    colorbar = plot.get_figure().get_axes()[1]
    colorbar.set_ylabel("Number of trips", fontsize=20)

    # Save the figure
    plt.savefig(f"{column}_cut.png" if is_cut else f"{column}.png", bbox_inches='tight')


def create_heat_map(shape_file: str) -> None:
    """
    Generates multiple heat maps from a shapefile showing the most
    frequently traveled routes for weekdays, weekends, and by scooter companies.

    Parameters
    ----------
    shape_file : str
        Path to the shapefile containing trip counts.

    Returns
    -------
    None
        Calls show_map multiple times and saves PNG maps.
    """
    # Load shapefile into a GeoDataFrame
    city_df: gpd.GeoDataFrame = gpd.read_file(shape_file)

    # Zoomed-in maps (cut) for different trip categories
    show_map(city_df, 'count_work', "Most frequent routes on weekdays (01.04.2023 - 30.04.2023)", is_cut=True)
    show_map(city_df, 'count_free', "Most frequent routes on weekends (01.04.2023 - 30.04.2023)", is_cut=True)
    show_map(city_df, 'count_lime', "Most frequent routes using Lime scooters (01.04.2023 - 30.04.2023)", is_cut=True)
    show_map(city_df, 'count_lyft', "Most frequent routes using Lyft scooters (01.04.2023 - 30.04.2023)", is_cut=True)
    show_map(city_df, 'count_link', "Most frequent routes using Link scooters (01.04.2023 - 30.04.2023)", is_cut=True)

    # Full maps (not cut) for different trip categories
    show_map(city_df, 'count_work', "Most frequent routes on weekdays (01.04.2023 - 30.04.2023)")
    show_map(city_df, 'count_free', "Most frequent routes on weekends (01.04.2023 - 30.04.2023)")
    show_map(city_df, 'count_lime', "Most frequent routes using Lime scooters (01.04.2023 - 30.04.2023)")
    show_map(city_df, 'count_lyft', "Most frequent routes using Lyft scooters (01.04.2023 - 30.04.2023)")
    show_map(city_df, 'count_link', "Most frequent routes using Link scooters (01.04.2023 - 30.04.2023)")
