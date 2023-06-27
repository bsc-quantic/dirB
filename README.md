# dirB

A generic tool working over HDF5 files to share experiments data, both input and output, in a standardized way.

JSON dictionaries are the default objects used within the HDF5 files in order to collect input parameters and resulting data.

## Features

[ToDo]

Example notebooks are added in this repository.

## Documentation

To generate the documentation, you should install sphinx and the proper theme plugin, and then run the make command for the HTML creation:

```
pip install sphinx sphinx_rtd_theme

cd docs
make html
```

With the following command we'll get a clean documentation env to regenerate the whole documentation in case we need to:

```
make clean html
make html
```