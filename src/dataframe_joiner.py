import geopandas as gpd

if __name__ == '__main__':
    # Read shapefiles for four different date ranges
    city_df_1 = gpd.read_file('../results/01-04-2023_07-04-2023/01-04-2023_07-04-2023.shp')
    city_df_2 = gpd.read_file('../results/08-04-2023_14-04-2023/08-04-2023_14-04-2023.shp')
    city_df_3 = gpd.read_file('../results/15-04-2023_21-04-2023/15-04-2023_21-04-2023.shp')
    city_df_4 = gpd.read_file('../results/22-04-2023_30-04-2023/22-04-2023_30-04-2023.shp')

    # Store all GeoDataFrames in a list
    dfs = [city_df_1, city_df_2, city_df_3, city_df_4]

    # Make a copy of the first GeoDataFrame to use as the base for aggregation
    result = dfs[0].copy()

    # Aggregate the numeric columns (columns 3 to 7) by summing across all GeoDataFrames
    # 'fill_value=0' ensures missing values are treated as 0 during the sum
    for df in dfs[1:]:
        result.iloc[:, 3:8] = result.iloc[:, 3:8].add(df.iloc[:, 3:8], fill_value=0)

    # Restore the original non-numeric columns from the first GeoDataFrame
    # These are usually identifiers or geometry columns that should not be aggregated
    result[['TYPE', 'NAME', 'ONEWAY', 'geometry']] = city_df_1[['TYPE', 'NAME', 'ONEWAY', 'geometry']]

    # Save the aggregated GeoDataFrame to a new shapefile
    result.to_file("01-04-2023_30-04-2023.shp")
