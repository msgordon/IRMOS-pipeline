#! /usr/bin/env python
import argparse
import pyfits
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.ndimage.filters import gaussian_filter1d

def rescale(x,y,minwave,maxwave,length):
    newx = np.linspace(minwave,maxwave,num = length)
    
    fy = interp1d(x,y, kind='slinear',bounds_error=False)
    
    #apply interp function to newx
    newy = fy(newx)
    
    return (newx,newy)

def is_normalized(header, normkey):
    #Return true if keyword 'normkey' is true in header
    if normkey in header and header[normkey]:
        return True
    else:
        return False

def normalize(data, header, key, normkey):
    #Divide image by exposure time keyword "key"
    #Update keyword "normkey" to True
    exptime = np.float(header[key])/1000.
    data /= exptime
    header[normkey] = (True, 'Data is normalized')
    
    return data, header

def getwaves(header, n):
    cdelt = header['CDELT1']
    crval = header['CRVAL1']
    x = np.arange(0,n)*cdelt + crval
    return x

def magnitude_flux(waves,mag,zeropt=48.60):
    #From Davenport
    #mag=-2.5*log(f_nu)-zeropt
    c = 2.99792458e18 # speed of light, in A/s
    flux = 10.0**( (mag + zeropt) / (-2.5) )
    
    #return flux in units (erg cm-2 s-1 A-1):
    return flux * (c / waves**2.0)

def smooth(spectrum, sigma):
    """Smooths the input spectrum using a user-specified Gaussian kernel.
    """
    spectrum = gaussian_filter1d(spectrum, sigma)
    return spectrum

def main():
    parser = argparse.ArgumentParser(description='Uses standard star data to flux-calibrate input spectra.')
    parser.add_argument('spec',type=str,help='Spectrum to flux-calibrate.')
    parser.add_argument('out',type=str,help='Name of output (calibrated) file.')
    parser.add_argument('std',type=str,help='Standard star spectrum.')
    parser.add_argument('sdat',type=str,help='Standard star data file.')
    parser.add_argument('-key', type=str, default='EXPTIME', help='Specify exposure time keyword (default=EXPTIME)')
    parser.add_argument('-normkey',type=str, default='NORM', help='Specify normalized keyword (default=NORM)')
    
    args=parser.parse_args()
    
    spec_counts = pyfits.getdata(args.spec)
    spec_hdr = pyfits.getheader(args.spec)
    std_counts = pyfits.getdata(args.std)
    std_hdr = pyfits.getheader(args.std)
    
    #Check to see if spec_hdr or std_hdr claim to be 2-dimensional
    if spec_hdr['NAXIS']==2:
        spec_counts = spec_counts[0]
    if std_hdr['NAXIS']==2:
        std_counts = std_counts[0]
    
    spec_waves = getwaves(spec_hdr, len(spec_counts))
    std_waves = getwaves(std_hdr, len(std_counts))
    
    sdat_waves, sdat_mag, sdat_wth = np.loadtxt(args.sdat, skiprows=1, unpack=True) #From Davenport
    
    #Convert mag units to flux units in sdat file
    sdat_flux = magnitude_flux(sdat_waves,sdat_mag)
    
    if is_normalized(spec_hdr, args.normkey)==False:
        spec_counts, spec_hdr = normalize(spec_counts, spec_hdr, args.key, args.normkey)
    if is_normalized(std_hdr, args.normkey)==False:
        std_counts, std_hdr = normalize(std_counts, std_hdr, args.key, args.normkey)
    
    #Removing zeroes to be safe (Feige15.fits has zeroes)
    zeroes = False
    zindex = []
    for i,thing in enumerate(std_counts):
        if thing==0:
            zeroes = True
            zindex = np.append(zindex, i)
    if zeroes==True:
        std_counts = np.delete(std_counts, zindex)
        std_waves = np.delete(std_waves, zindex)
    
    #Smooth std spectrum to effectively simulate background continuum
    '''sigma = 400
    
    std_counts_smoothed = smooth(std_counts, sigma)'''
    
    #Rescale calibration spectrum to be same length and scale as standard star spectrum
    sdat_waves, sdat_flux = rescale(sdat_waves, sdat_flux, np.min(std_waves), np.max(std_waves), len(std_waves))
    
    #Create sensitivity function
    ratio = np.abs(np.array(sdat_flux,dtype='float')/np.array(std_counts,dtype='float')) #From Davenport
    
    
    
    #Update spectrum header
    spec_hdr['FCAL'] = (True, 'Data is flux-calibrated')
    
    #Write flux-calibrated sprectrum to .fits file
    pyfits.writeto(ars.out, spec_flux, spec_hdr, clobber=True)
    

if __name__ == '__main__':
    main()
