from lltiler import LLTiler
import matplotlib.pylab as plt

# This example uses colors from a matplotlib colormap to create the colors
# of the generated tiles.

lat_min = 10.
lon_min = 45.
lat_max = 15.
lon_max = 48.

cmap = plt.get_cmap("viridis")


def f(lat, lon):
    rel_lat = (lat - lat_min) / (lat_max - lat_min)
    rel_lon = (lon - lon_min) / (lon_max - lon_min)
    valid = (rel_lat >= 0) & (rel_lat < 1) & (rel_lon >= 0) & (rel_lon < 1)
    colors = cmap(rel_lat, bytes=True)
    colors[..., -1] = 255 * valid
    return colors


t = LLTiler("temp_maps/gray", base_level=8)
# t = LLTiler("temp_maps/gray", size_hint=1000.)
# note that show_progress=True requires tqdm
t.render(((lat_min, lon_min), (lat_max, lon_max)), f, show_progress=False)
