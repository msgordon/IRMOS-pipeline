#! /usr/bin/env python
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pyfits
from scipy.interpolate import interp1d
from math import sqrt


def Header(header,sub_tf,xwav,name):
    head=header
    
    xpix=np.arange(1,len(xwav)+1)
    z=np.polyfit(xpix,xwav,1)
    p=np.poly1d(z)
    
    head['CDELT1']=z[0]
    head['CRPIX1']=1
    head['CRVAL1']=p(1)
    head['SKYSUB']=sub_tf
    head['SKYREF']=name+'_specsky.fits'
    return head


def rescale(x,y,minwave,maxwave):
    # newx same length as original spectrum, but rescaled
    newx = np.linspace(minwave,maxwave,num = len(x))
    
    fy = interp1d(x,y, kind='slinear',bounds_error=False)
    
    #apply interp function to newx
    newy = fy(newx)
    
    return (newx,newy)

def main():
    parser = argparse.ArgumentParser(description='Takes two spectra files and subtracts them, then gives the resulting RMS.')
    parser.add_argument('filename',type=str,help='File location and handle for the spectra (e.g. NGC253_spec).')
    parser.add_argument('wrange',nargs=2,type=int,help='Wavelength range in Angstroms (Enter 2 numbers, low and high).')
    
    args=parser.parse_args()
    
    ydata,header  = pyfits.getdata(args.filename, header=True)

    xdata = np.arange(0,len(ydata))*header['CDELT1']+header['CRVAL1']
    
    min_wave = np.min([np.min(x) for x in xdata])
    max_wave = np.max([np.max(x) for x in xdata])
    newspecs = rescale(xdata,ydata,min_wave,max_wave)
    x = newspecs[0]
    y = newspecs[1]
    yvals=np.array([y[i] for i,j in enumerate(x) if j>=args.wrange[0] and j<=args.wrange[1]])

    rms=np.sqrt(np.sum(n*n for n in yvals)/float(len(yvals)))
    
    print "RMS is: %f" % rms
    print "Mean is: %f" % np.mean(yvals)

    print "mean/rms: %f" % (np.mean(yvals)/rms)
    

    """
    print np.min(xnew[0])
    print np.diff(xnew[0])


    header = pyfits.getheader(args.specimgs+'%i.fits' % args.spec1)
    header['CRVAL'] = np.min(xnew[0])
    header['CDELT1'] = np.diff(xnew[0])[0]
    pyfits.writeto('OMC_specskysub.test.fits',ysub,header=header)
    #"""
    
    #plt.plot(x, y)
    #plt.show()

if __name__ == '__main__':
    main()
