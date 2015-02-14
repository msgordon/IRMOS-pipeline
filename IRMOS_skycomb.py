#! /usr/bin/env python
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pyfits
from scipy.interpolate import interp1d

def rescale(x,y,minwave,maxwave):
    # newx same length as original spectrum, but rescaled
    newx = np.linspace(minwave,maxwave,num = len(x))

    fy = interp1d(x,y, kind='slinear',bounds_error=False)

    #apply interp function to newx
    newy = fy(newx)

    return (newx,newy)

def main():
    parser = argparse.ArgumentParser(description='Aligns all spectra, combines sky spectra, and writes a fits file for the new sky spectrum and each object spectrum.')
    parser.add_argument('specimgs',type=str,help='File location and handle for the spectra (e.g. NGC253_spec).')
    parser.add_argument('specmin',type=int,help='Number of first aperture (usually 0).')
    parser.add_argument('objmin',type=int,help='Number of first object aperture.')
    parser.add_argument('objmax',type=int,help='Number of last object aperture.')
    parser.add_argument('specmax',type=int,help='Number of last aperture.')
    
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
    
    min_wave = np.min([np.min(x) for x in xdata])
    max_wave = np.max([np.max(x) for x in xdata])

    xnew, ynew = [rescale(xdata[i],ydata[i],min_wave,max_wave) for i in range(0,len(xdata))]
    
    #Write the obj spectra files here...
    
    yskyspecs=np.array([y for y in ynew if y<args.objmin or y>args.objmax])
    ysky=np.nanmean(yskyspecs,axis=0)
    

if __name__ == '__main__':
    main()
