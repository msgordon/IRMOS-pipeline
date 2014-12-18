#! /usr/bin/env python
import argparse
import pyfits
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
from target_utils import targets_from_region

#########
### Gaussian smoothing
#########
def smooth(y,sigma=3):
    return gaussian_filter1d(y,sigma=sigma)


def main():
    parser = argparse.ArgumentParser(description='Builds a flat-field image from an input flat and region file.')
    parser.add_argument('flat',type=str,help='Image file from which to build flatfield')
    parser.add_argument('reg',type=str,help='Input region file defining apertures.')
    parser.add_argument('out',type=str,help='Output flat-field image.')
    parser.add_argument('--s',metavar='sigma',type=float,default=3.0,help='Specify sigma size for Gaussian smoothing.')
    parser.add_argument('--c',action='store_true',help='Clobber on output')

    args = parser.parse_args()
    print 'Parsing apertures from %s' % args.reg
    targets = targets_from_region(args.reg)
    print '\t%i aperture%s found' % (len(targets),'' if len(targets) == 1 else 's')

    # Flat-field each target region by Gaussian smoothing
    print 'Smoothing flat fields from %s' % args.flat
    FLAT_field, header = pyfits.getdata(args.flat,header=True)

    FLAT_field = FLAT_field.astype(np.float)

    # BLANK will store the new array
    BLANK = np.ones(FLAT_field.shape)

    # Note: x and y are switched from image coordinates
    for target in targets:
        # Median squish the aperture
        aperture = FLAT_field[target[1]:target[0],:]
        ap_blank = BLANK[target[1]:target[0],:]

        y = np.median(aperture, axis=0)

        # Smooth squish
        smoothed = smooth(y, args.s)
    
        # For each row in aperture, divide by smoothed fit
        for col in range(0,aperture.shape[0]):
            aperture[col,:] /= smoothed

        ap_blank[:,:] = aperture
            
    # Write flatfield to file
    header['FLATREF'] = (args.flat,'Flat before smoothed')
    header['FLATFLD'] = (True, 'Image is flatfield')
    header['FLATSIG'] = (args.s,'Flat Gaussian smooth sigma')
    header['NAME'] = args.out
    
    print 'Writing flat field to %s' % args.out
    pyfits.writeto(args.out, BLANK, header=header,clobber=args.c)


if __name__ == '__main__':
    main()
