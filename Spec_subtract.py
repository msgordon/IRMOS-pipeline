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
    parser.add_argument('specimgs',type=str,help='File location and handle for the spectra (e.g. NGC253_spec).')
    parser.add_argument('spec1',type=int,help='Number of first aperture.')
    parser.add_argument('spec2',type=int,help='Number of second aperture.')
    parser.add_argument('wrange',nargs=2,type=int,help='Wavelength range in Angstroms (Enter 2 numbers, low and high).')
    parser.add_argument('-stats',action='store_true',default=False)
    
    args=parser.parse_args()
    
    ydata=[]
    ydata.append(pyfits.getdata(args.specimgs+'%i.fits' % args.spec1))
    ydata.append(pyfits.getdata(args.specimgs+'%i.fits' % args.spec2))
    ydata=np.array(ydata)
    
    heads=[]
    heads.append(pyfits.getheader(args.specimgs+'%i.fits' % args.spec1))
    heads.append(pyfits.getheader(args.specimgs+'%i.fits' % args.spec2))
    
    xdata=[]
    xdata.append(np.arange(0,len(ydata[0]))*heads[0]['CDELT1']+heads[0]['CRVAL1'])
    xdata.append(np.arange(0,len(ydata[1]))*heads[1]['CDELT1']+heads[1]['CRVAL1'])
    xdata=np.array(xdata)
    
    min_wave = np.min([np.min(x) for x in xdata])
    max_wave = np.max([np.max(x) for x in xdata])
    
    newspecs = [rescale(xdata[i],ydata[i],min_wave,max_wave) for i,spec in enumerate(xdata)]
    xnew=[]
    ynew=[]
    for spec in newspecs:
        xnew.append(spec[0])
        ynew.append(spec[1])
    xnew=np.array(xnew)
    ynew=np.array(ynew)
    
    ysub=ynew[0]-ynew[1]

    if not args.stats:
        pyfits.writeto('test_sub.fits',ysub,Header(heads[0],'',xnew[0],'test_sub.fits'),clobber=True)

    else:
        ysub=ynew[1]
    yvals=np.array([ysub[i] for i,j in enumerate(xnew[0]) if j>=args.wrange[0] and j<=args.wrange[1]])
    rms=sqrt(sum(n*n for n in yvals)/float(len(yvals)))
    
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
    
    plt.plot(xnew[0], ysub)
    plt.show()

if __name__ == '__main__':
    main()
