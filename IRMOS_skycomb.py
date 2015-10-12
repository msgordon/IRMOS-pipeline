#! /usr/bin/env python
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pyfits
from scipy.interpolate import interp1d
import sys

def getwaves(header, n):
    cdelt = header['CDELT1']
    crval = header['CRVAL1']

    x = np.arange(0,n)*cdelt + crval
    return x

def rescale(x,y,minwave,maxwave):
    # newx same length as original spectrum, but rescaled
    newx = np.linspace(minwave,maxwave,num = len(x))

    fy = interp1d(x,y, kind='slinear',bounds_error=False)

    #apply interp function to newx
    newy = fy(newx)

    return (newx,newy)

def main():
    parser = argparse.ArgumentParser(description='Aligns all spectra, combines sky spectra, and writes a fits file for the new sky spectrum and each object spectrum.')
    parser.add_argument('skyfiles',nargs='+',help='List of sky spectra to combine.')
    parser.add_argument('outsky',type=str,help='Output file')
    parser.add_argument('--c',action='store_true',help='If specified, overwrite')
    
    args = parser.parse_args()
    if len(args.skyfiles) < 2:
        sys.exit('Error: At least two skyfiles required for combining')

    ydata = []
    xdata = []
    hdrs = []
    for skyfile in args.skyfiles:
        y,h = pyfits.getdata(skyfile, header=True)
        ydata.append(y)
        hdrs.append(h)

        x = getwaves(h, len(y))
        xdata.append(x)

    ydata = np.array(ydata)
    xdata = np.array(xdata)

    min_wave = np.min([np.min(row) for row in xdata])
    max_wave = np.max([np.max(row) for row in xdata])

    print 'Combining spectra'
    newspecs = [rescale(xdata[i],ydata[i],min_wave,max_wave) for i,spec in enumerate(xdata)]

    xnew = []
    ynew = []
    for spec in newspecs:
        xnew.append(spec[0])
        ynew.append(spec[1])
    xnew = np.array(xnew)
    ynew = np.array(ynew)
    
    ysky = np.nanmean(ynew,axis=0)
    xsky = xnew[0]
    header = hdrs[0]
    header['CDELT1'] = np.diff(xsky)[0]
    header['CRVAL1'] = np.min(xsky)

    print 'w0: %.2f, w1: %.2f, dw: %.2f' % (min_wave,max_wave,header['CDELT1'])

    print 'Writing to %s' % args.outsky
    #pyfits.writeto(args.outsky,ysky,header,clobber=args.c)
    
    

if __name__ == '__main__':
    main()
