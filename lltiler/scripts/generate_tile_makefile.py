import os
from collections import defaultdict


def find_tiles(tiledir):
    for xdir in os.listdir(tiledir):
        try:
            x = int(xdir)
        except ValueError:
            continue
        for filename in os.listdir(os.path.join(tiledir, xdir)):
            base, ext = os.path.splitext(filename)
            y = int(base)
            yield (x, y)


def make_pyramides(basedir, level, tiles):
    if level == 0:
        return
    tiles = set(tiles)
    next_tiles = set((int(x/2), int(y/2)) for x, y in tiles)

    def intile_name(x, y):
        if (x, y) in tiles:
            return os.path.join(basedir, str(level), str(x), "%d.png" % y)
        else:
            return "-"

    def outtile_name(x, y):
        return os.path.join(basedir, str(level-1), str(x), "%d.png" % y)

    for x, y in next_tiles:
        innames = [intile_name(2*x+sx, 2*y+sy)
                   for sx, sy in [(0, 0), (0, 1), (1, 0), (1, 1)]]
        indeps = [inname for inname in innames if inname != "-"]
        print(outtile_name(x, y) + ": " + (" ".join(indeps)))
        print("\t${PYRAMID_STEP} $@ " + (" ".join(innames)))
        print()
    make_pyramides(basedir, level-1, next_tiles)


def _main(from_setuptools_script=True):
    import sys
    if from_setuptools_script:
        pyramid_step = "pyramid_step"
        overlay_tiles = "overlay_tiles"
    else:
        script_base_dir = os.path.abspath(os.path.dirname(__file__))
        pyramid_step = "\"{}\" \"{}\"".format(
                sys.executable,
                os.path.join(script_base_dir, "pyramid_step.py"))
        overlay_tiles = "\"{}\" \"{}\"".format(
                sys.executable,
                os.path.join(script_base_dir, "overlay_tiles.py"))

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("base_level",
                        type=int,
                        help="level in which input tiles have been generated")
    parser.add_argument("base_dir",
                        type=str,
                        help="folder containing input tiles")
    parser.add_argument("out_dir",
                        type=str,
                        help="folder for generated output tiles")
    args = parser.parse_args()

    base_level = args.base_level
    basedir = args.base_dir
    outdir = args.out_dir
    layers = sorted(os.listdir(basedir))
    layers_by_tile = defaultdict(list)
    for layer in layers:
        for tile in find_tiles(os.path.join(basedir, layer, str(base_level))):
            layers_by_tile[tile].append(layer)

    def outname(x, y):
        return os.path.join(outdir,
                            str(base_level), str(x), str(y) + ".png")

    def inname(layer, x, y):
        return os.path.join(basedir, layer,
                            str(base_level), str(x), str(y) + ".png")

    yvals_by_x = defaultdict(list)
    for x, y in layers_by_tile.keys():
        yvals_by_x[x].append(y)

    print("PYRAMID_STEP={}".format(pyramid_step))
    print("OVERLAY_TILES={}".format(overlay_tiles))
    print()
    print("all: " + os.path.join(outdir, "0", "0", "0.png"))
    print(".PHONY: all")
    print()
    make_pyramides(outdir, base_level, layers_by_tile.keys())
    for (x, y), layers in sorted(layers_by_tile.items()):
        print(outname(x, y) + ": " + (" ".join(inname(layer, x, y)
                                               for layer in sorted(layers))))
        print("\t${OVERLAY_TILES} $@ $^")
        print()


if __name__ == '__main__':
    _main(False)
