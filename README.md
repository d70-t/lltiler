# lltiler
The Lat-Lon Tiler is a small tool to create map tiles in spherical Mercator projection for the use with online map libraries like Leaflet, OpenLayers, Mapbox etc...

## usage
In order to create tiles with lltiler, the user must provide a function which can compute colors for given pairs of latitude and longitude.
A typical example would be a function which interpolates an image onto the given latitudes and longitudes.
This method is used to generate the most detailed level of tiles in a first step.
In an optional second step, multiple tile sets generated using `LLTiler` can be combined using the `overlay_tiles` utility.
In the last step, coarsened tiles are generated in successive steps from the most detailed level up to global scale using the `pyramid_step` utility.
The second and third step can be executed automatically using the `generate_tile_makefile` utility and GNU make.

### 1 generate detailed tiles
A user supplied function and a lat/lon bounding box must then be handed to the render method of the `LLTiler` object, which will then compute the necessary tiles and calls the given function repeatedly until all tiles have been generated.
An example is shown below:

```python
from lltiler import LLTiler
import matplotlib.pylab as plt
import matplotlib.colorbar

lat_min = 16.
lon_min = 45.
lat_max = 19.
lon_max = 48.

cmap = plt.get_cmap("gray")

def f(lat, lon):
    rel_lat = (lat - lat_min) / (lat_max - lat_min)
    rel_lon = (lon - lon_min) / (lon_max - lon_min)
    valid = (rel_lat >= 0) & (rel_lat < 1) & (rel_lon >= 0) & (rel_lon < 1)
    colors = cmap(rel_lat, bytes=True)
    colors[..., -1] = 255 * valid
    return colors

t = LLTiler("temp_maps/gray", size_hint=1000.)
t.render(((lat_min, lon_min), (lat_max, lon_max)), f, show_progress=True)
```

Note that `show_progress=True` additionally requires the `tqdm` package.

### 2 (optional) combine multiple overlapping tiles
If multiple tilesets have been generated using the first step and these tilesets should be combined to one tileset, the `overlay_tiles` utility can be used to paint multiple images on top of each other.
This is of course only useful if the image which is painted on top contains transparent regions where parts of the lower image can be seen through.

```bash
overlay_tiles <output_image> <input_image_1> <input_image_2> ... <input_image_n>
```

### 3 generate image pyramid
To generate coarser resolution images from detailed images, the `pyramid_step` utility can be used.
It takes up to four adjacent images (missing images are assumed to be entirely transparent) stacks these images together and generates a new image with half of the original resolution.

```bash
pyramid_step <output_image> <top_left> <bottom_left> <top_right> <bottom_right>
```

Missing images must be denoted by a `-`.


### automate steps 2 and 3
The `generate_tile_makefile` utility can be used to automate steps 2 and 3:

```bash
generate_tile_makefile <base_level> <input_folder> <output_folder> | make -f- -j
```

`base_level` must be the tile-level for which the tiles have been generated in step 1.
`input_folder` must be a folder which includes one folder per input tileset.
`output_folder` is the folder into which the resulting tiles should be written.

Note that in the above command generates a makefile which is directly passed to make and then executed in parallel.
