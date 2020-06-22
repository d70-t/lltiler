from lltiler import LLTiler
import matplotlib.pylab as plt
import matplotlib.colorbar

t = LLTiler("./test", base_level=7)

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
    colors[...,-1] = 255 * valid
    return colors

t.render(((lat_min, lon_min), (lat_max, lon_max)), f, show_progress=True)
