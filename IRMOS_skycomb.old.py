#! /usr/bin/env python
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pyfits
from scipy.interpolate import interp1d

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
    parser = argparse.ArgumentParser(description='Aligns all spectra, combines sky spectra, and writes a fits file for the new sky spectrum and each object spectrum.')
    parser.add_argument('specimgs',type=str,help='File location and handle for the spectra (e.g. NGC253_spec).')
    parser.add_argument('name',type=str,help='Name of data set (e.g. NGC253).')
    parser.add_argument('specmin',type=int,help='Number of first aperture (usually 0).')
    parser.add_argument('specmax',type=int,help='Number of last aperture.')
    parser.add_argument('-obj',nargs='+',type=int,help='Object aperture numbers.')
    
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
    
    newspecs = [rescale(xdata[i],ydata[i],min_wave,max_wave) for i,spec in enumerate(xdata)]
    xnew=[]
    ynew=[]
    for spec in newspecs:
        xnew.append(spec[0])
        ynew.append(spec[1])
    xnew=np.array(xnew)
    ynew=np.array(ynew)
    
    #Following steps are updated to accommodate for cases in which specmin is non-zero.
    
    for obj in args.obj:
        pyfits.writeto('%s%i_r.fits' % (args.specimgs, obj), ynew[obj-args.specmin], Header(heads[obj-args.specmin], False, xnew[obj-args.specmin], args.name), clobber=True)
    
    yskyspecs=np.array([y for i,y in enumerate(ynew) if i+args.specmin not in args.obj])
    ysky=np.nanmean(yskyspecs,axis=0)
    pyfits.writeto('%s%s' % (args.specimgs,'sky.fits'), ysky, Header(heads[0],False,xnew[0],args.name), clobber=True)
    
    for obj in args.obj:
        skysub=ynew[obj-args.specmin]-ysky
        pyfits.writeto('%s%i_skysub.fits' % (args.specimgs, obj), skysub, Header(heads[obj-args.specmin], True, xnew[obj-args.specmin], args.name), clobber=True)
    

if __name__ == '__main__':
    main()
