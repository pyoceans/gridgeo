
from docopt import docopt

from gridgeo import GridGeo

__doc__ = """
Save a GeoJSON or ESRI Shapefile representation of an ocean model grid.

Usage:
    gridio URL VAR --output=OUTFILE

    gridio (-h | --help -o | --output)

Examples:
    gridio netcdf-file.nc sea_water_temperature --output=grid.shp
    gridio remote-opendap-url sea_water_temperature --output=grid.geojson

Arguments:
  directory               Configuration directory.

Options:
  -h --help                       Show this screen.
  -o OUTFILE --output=OUTFILE     Output file
"""


def parse_args():
    args = docopt(__doc__)
    return args


def cli(args):
    url = args.get('URL')
    standard_name = args.get('VAR')
    filename = args.get('--output')

    grid = GridGeo(url, standard_name=standard_name)
    grid.save(filename, float_precision=4)


def main():
    args = parse_args()
    cli(args)


if __name__ == '__main__':
    main()
