#! /usr/bin/env python
import argparse
import pyfits
import matplotlib.pyplot as plt
from IRMOS_plotter import Plotter


def main():
    parser = argparse.ArgumentParser(description='Identify spectral features in input file')
    parser.add_argument('image',type=str,help='Single or multi-aperture FITS file')
    parser.add_argument('linelist',type=str,help='Linelist of features')
    parser.add_argument('-a',type=int,default=0,help='Start at specified aperture (default=0)')

    args = parser.parse_args()

    data,header = pyfits.getdata(args.image, header=True)

    # open initial aperture
    #ap = data[args.a]

    plotter = Plotter(args.image, args.a, args.linelist)
    plotter.show()


if __name__ == '__main__':
    main()
