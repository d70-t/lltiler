from PIL import Image

TILE_SIZE = 256


def combine(tl, bl, tr, br):
    new_image = Image.new("RGBA", (2*TILE_SIZE, 2*TILE_SIZE), (0, 0, 0, 0))
    for xofs, yofs, subtile in [(0, 0, tl),
                                (1, 0, tr),
                                (0, 1, bl),
                                (1, 1, br)]:
        new_image.paste(subtile,
                        box=(xofs*TILE_SIZE, yofs*TILE_SIZE,
                             (xofs+1)*TILE_SIZE, (yofs+1)*TILE_SIZE))
    new_image.thumbnail((TILE_SIZE, TILE_SIZE), Image.LANCZOS)
    return new_image


def load_file(path):
    if path == "-":
        return Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    else:
        return Image.open(path)


def _main():
    import os
    import sys
    outfile = sys.argv[1]
    infiles = sys.argv[2:]
    assert len(infiles) == 4
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        try:
            os.makedirs(outdir)
        except OSError:
            # catch race condition, if folder is created in between both calls
            pass
    outimage = combine(*map(load_file, infiles))
    outimage.save(outfile)


if __name__ == '__main__':
    _main()
