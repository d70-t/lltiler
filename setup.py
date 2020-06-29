import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lltiler",
    version="0.0.1",
    author="Tobias Kölling",
    author_email="tobias.koelling@physik.uni-muenchen.de",
    description=(
        "The Lat-Lon Tiler is a small tool to create map tiles in spherical"
        "mercator projection for the use with online map libraries like"
        "Leaflet, OpenLayers, Mapbox etc..."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/d70-t/lltiler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    install_requires=[
        "numpy",
        "pillow",
    ],
    entry_points={
        "console_scripts": [
            "{0} = lltiler.scripts.{0}:_main".format(script)
            for script in ["overlay_tiles",
                           "pyramid_step",
                           "generate_tile_makefile"]
        ],
    },
)
