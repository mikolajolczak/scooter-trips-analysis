import geopandas as gpd
import matplotlib.pyplot as plt



def show_map(geodataframe, column, title="Mapa"):
    fig, ax = plt.subplots(1, 1, figsize=(30, 20))

    def get_linewidth(value):
        return 2 if value > 0 else 0.5

    linewidths = geodataframe[column].apply(get_linewidth)

    plot = geodataframe.plot(ax=ax, column=column, legend=True, cmap='plasma', linewidth=linewidths)
    ax.set_ylim((41.66013746994182, 42.00962338))
    ax.set_xlim((-87.80370076, -87.5349023379022))
    ax.set_title(title, fontsize=30)

    colorbar = plot.get_figure().get_axes()[1]
    colorbar.set_ylabel("Liczba przejazdów", fontsize=20)

    plt.savefig(f"{column}.png", bbox_inches='tight')


if __name__ == '__main__':
    city_df = gpd.read_file('../results/01-04-2023_30-04-2023.shp')
    show_map(city_df, 'count_work', "Najczęsciej uczęstrzane trasy w dni robocze w okresie 01.04.2023 - 30.04.2023")
    show_map(city_df, 'count_free', "Najczęsciej uczęstrzane trasy w dni wolne w okresie 01.04.2023 - 30.04.2023")
    show_map(city_df, 'count_lime', "Najczęsciej uczęstrzane trasy przy użyciu sprzętu firmy Lime w okresie 01.04.2023 - 30.04.2023")
    show_map(city_df, 'count_lyft', "Najczęsciej uczęstrzane trasy przy użyciu sprzętu firmy Lyft w okresie 01.04.2023 - 30.04.2023")
    show_map(city_df, 'count_link', "Najczęsciej uczęstrzane trasy przy użyciu sprzętu firmy Link w okresie 01.04.2023 - 30.04.2023")