import geopandas as gpd
if __name__ == '__main__':
    city_df_1 = gpd.read_file('../results/01-04-2023_07-04-2023/01-04-2023_07-04-2023.shp')
    city_df_2 = gpd.read_file('../results/08-04-2023_14-04-2023/08-04-2023_14-04-2023.shp')
    city_df_3 = gpd.read_file('../results/15-04-2023_21-04-2023/15-04-2023_21-04-2023.shp')
    city_df_4 = gpd.read_file('../results/22-04-2023_30-04-2023/22-04-2023_30-04-2023.shp')
    dfs = [city_df_1, city_df_2, city_df_3, city_df_4]
    result = dfs[0].copy()
    for df in dfs[1:]:
        result.iloc[:, 3:8] = result.iloc[:, 3:8].add(df.iloc[:, 3:8], fill_value=0)
    result[['TYPE', 'NAME', 'ONEWAY', 'geometry']] = city_df_1[['TYPE', 'NAME', 'ONEWAY', 'geometry']]
    result.to_file("01-04-2023_30-04-2023.shp")