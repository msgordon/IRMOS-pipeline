#! /usr/bin/env python
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pyfits
import ConfigParser

def main():
    parser = argparse.ArgumentParser(description='Aligns all spectra, combines sky spectra, and writes a fits file for the new sky spectrum and each object spectrum.')
    parser.add_argument('specimgs',type=str,help='File location and handle for the spectra (e.g. NGC253_spec).')
    parser.add_argument('specmin',type=int,help='Number of first aperture (usually 0).')
    parser.add_argument('objmin',type=int,help='Number of first object aperture.')
    parser.add_argument('objmax',type=int,help='Number of last object aperture.')
    parser.add_argument('specmax',type=int,help='Number of last aperture.')
    parser.add_argument('wavemin',type=int,help='Wavelength(A) in the empty space before the spectra (for cut-off).')
    parser.add_argument('wavemax',type=int,help='Wavelength(A) in the empty space after the spectra (for cut-off).')
    
    args=parser.parse_args()
    
    ydata=[]
    for num in range(args.specmin, args.specmax+1):
        ydata.append(pyfits.getdata(args.specimgs+'%i.fits' % num))
    ydata=np.array(ydata)
    
    heads=[]
    for num in range(args.specmin, args.specmax+1):
        heads.append(pyfits.getheader(args.specimgs+'%i.fits' % num))
    
    xdata=[]
    for i,num in enumerate(range(args.specmin, args.specmax+1)):
        xdata.append(np.arange(0,len(ydata[i]))*heads[i]['CDELT1']+heads[i]['CRVAL1'])
    xdata=np.array(xdata)
    
    ydnew=[]
    xdnew=[]
    for i,spec in enumerate(xdata):
        ytemp=[]
        xtemp=[]
        for j,thing in enumerate(spec):
            if thing > args.wavemin and thing < args.wavemax:
                xtemp.append(thing)
                ytemp.append(ydata[i][j])
        ydnew.append(ytemp)
        xdnew.append(xtemp)
    
    ydnew=np.array(ydnew)
    xdnew=np.array(xdnew)
    
    print len(xdnew)
    
    print len(ydnew)
    
    for spec in xdnew:
        print len(spec)
    
    for spec in ydnew:
        print len(spec)

if __name__ == '__main__':
    main()
