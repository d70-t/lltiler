from PIL import Image


def overlay(images):
    if len(images) == 1:
        return images[0]
    new_image = Image.new("RGBA", images[0].size, (0, 0, 0, 0))
    for image in images:
        new_image.paste(image, None, image)
    return new_image


def _main():
    import os
    import sys
    outfile = sys.argv[1]
    infiles = sys.argv[2:]
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        try:
            os.makedirs(outdir)
        except OSError:
            # catch race condition, if folder is created in between both calls
            pass
    new_im = overlay(list(map(Image.open, infiles)))
    new_im.save(outfile)


if __name__ == '__main__':
    _main()
