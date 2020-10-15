import os
import itertools
import numpy as np
from PIL import Image


def numTiles(z):
    return 2**z


def resolution2zoom(res, lat=0., tilesize=256):
    """
    computes zoom level corresponsing to a given desired resolution
    :param res: desired resolution in meters
    :param lat: lowest absolute latitude value of desired scene
    :param tilesize: size of one tile in pixels

    :see: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Resolution_and_Scale # noqa: E501
    """
    zoom0_pixel_size = 40075016.686 / tilesize
    return np.log2(zoom0_pixel_size * np.cos(np.deg2rad(lat)) / res)


def latlon2relativeXY(lat, lon):
    x = (lon + 180) / 360
    rlat = np.deg2rad(lat)
    y = (1 - np.log(np.tan(rlat) + 1./np.cos(rlat)) / np.pi) / 2
    return x, y


def latlon2xy(lat, lon, z):
    n = numTiles(z)
    x, y = latlon2relativeXY(lat, lon)
    return n*x, n*y


def mercatorToLat(mercatorY):
    return np.rad2deg(np.arctan(np.sinh(mercatorY)))


def xy2latlon(x, y, z):
    n = numTiles(z)
    rel_y = y / n
    lat = mercatorToLat(np.pi * (1 - 2 * rel_y))
    lon = -180.0 + 360.0 * x / n
    return lat, lon


def render_tile(x, y, z, callback, tilesize=256):
    ys = ((np.arange(tilesize) + .5) / tilesize)[:, np.newaxis]
    xs = ys.T
    xs, ys = np.broadcast_arrays(x + xs, y + ys)
    lat, lon = xy2latlon(xs, ys, z)
    return callback(lat, lon)


class TileSelector:
    pass


class AllTileSelector(TileSelector):
    """
    Selects all tiles
    """
    def len(self, total):
        return total

    def select(self, tilegen):
        return tilegen


class ChunkTileSelector(TileSelector):
    def __init__(self, num_chunks, chunk):
        """
        Selects tiles based on chunks.

        All tiles are split into `num_chunk` approximately equally sized chunks
        but only the tiles belonging to chunk no `chunk` are selected.
        """
        self.num_chunks = num_chunks
        self.chunk = chunk

    def len(self, total):
        rem = total % self.num_chunks
        sub = total // self.num_chunks
        if self.chunk < rem:
            sub += 1
        return sub

    def select(self, tilegen):
        return itertools.islice(tilegen, self.chunk, None, self.num_chunks)


class LLTiler:
    def __init__(self,
                 data_folder,
                 base_level=None,
                 size_hint=None,
                 naming_scheme="{z}/{x}/{y}.png"):
        """
        :param data_folder: folder to store tiles
        :param base_level: level in which tiles should be computed
        :param size_tint: smallest size meters to be resolved
        :param naming_scheme: pattern for tilenames,
                              must include x, y and z placeholders

        :note: either `base_level` or `size_hint` must be given
        """
        self.data_folder = data_folder
        if base_level is None:
            if size_hint is None:
                raise ValueError(
                        "either base_level or size_hint must be given")
        self.size_hint = size_hint
        self.base_level = base_level

        self.naming_scheme = naming_scheme

    def render(self, extent, callback, show_progress=False, selector=AllTileSelector()):
        """
        :param extent: ((lat_min, lon_min), (lat_max, lon_max))
        :param callback: function accepting lat and a lon array
                         and returns RGBA values
        """

        if show_progress:
            from tqdm import tqdm
            progress = tqdm
        else:
            def progress(x, total):
                return x

        (lat_min, lon_min), (lat_max, lon_max) = extent

        if lat_min * lat_max < 0:
            lat_abs_min = 0.
        else:
            lat_abs_min = min(abs(lat_min), abs(lat_max))

        if self.base_level is None:
            self.base_level = int(np.ceil(resolution2zoom(
                self.size_hint, lat_abs_min)))

        x1, y1 = latlon2xy(lat_min, lon_min, self.base_level)
        x2, y2 = latlon2xy(lat_max, lon_max, self.base_level)

        x_min = int(min(x1, x2))
        x_max = int(max(x1, x2))
        y_min = int(min(y1, y2))
        y_max = int(max(y1, y2))

        total = selector.len((x_max - x_min + 1) * (y_max - y_min + 1))

        for x, y in progress(selector.select(
                itertools.product(range(x_min, x_max + 1), range(y_min, y_max + 1))),
                total=total):
            tile = render_tile(x, y, self.base_level, callback)
            if np.any(tile[..., -1] != 0):  # check if all transparent
                self.store_tile(tile, x, y, self.base_level)

    def tile_path(self, x, y, z):
        return os.path.join(self.data_folder,
                            self.naming_scheme.format(x=x, y=y, z=z))

    def store_tile(self, tile, x, y, z):
        filename = self.tile_path(x, y, z)
        folder = os.path.dirname(filename)
        os.makedirs(folder, exist_ok=True)
        image = Image.fromarray(tile)
        image.save(filename)
