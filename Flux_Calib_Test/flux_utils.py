#! /usr/bin/env python

"""
11/16/2015

Utility modules that may or not be useful for fluxcalibration
"""

import argparse
import numpy as np
import pyfits
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d
from peakdetect import peakdetect
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline as USplineFit

def plot_spectrum(wave, spectrum, color='k',ax=None,ls='-',title=None,xlim=None,ylim=None):

    if ax is None:
        ax = plt.figure().gca()
    if ls in ['-','--']:
        handle = ax.plot(wave,spectrum, ls=ls, lw=1.5, color=color)
    else:
        handle = ax.plot(wave,spectrum, ls='None',marker=ls,color=color)
        
    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)
    
    plt.xlabel('$\lambda$ ($\AA$)', fontsize=16)
    ax.tick_params(axis='x', which='both', labelsize=16)
    ax.tick_params(axis='y', which='both')

    plt.tight_layout()
    if title:
        plt.title(title)

    return ax


def get_spectrum(filename):
  """Read spectrum using pyfits.  Returns spectrum and header.
  """
  spectrum, header = pyfits.getdata(filename, 0, header=True)

  if len(spectrum) != int(header['naxis1']):
    spectrum = spectrum[0]

  
  lambda1 = header['crval1']
  lambda2 = float(header['naxis1'])*header['cdelt1']+float(header['crval1'])

  wave = np.arange(lambda1, lambda2, header['cdelt1'])
  wave = wave[:len(spectrum)]
 
  return (header, wave, spectrum)



def smooth(spectrum, kernel=0):
  """Smooths the input spectrum using a user-specified Gaussian kernel.
  """

  spectrum = gaussian_filter1d(spectrum, sigma=kernel)

  return spectrum


def find_lines(y,x_axis=None,lookahead=50):
    localmax,localmin = peakdetect(y,x_axis=x_axis,lookahead=lookahead/4)

    xmin, minval = zip(*localmin)
    xmax, maxval = zip(*localmax)

    # cat lists
    x = np.concatenate((xmin,xmax))
    y = np.concatenate((minval,maxval))
    return x,y

def gauss_function(x, a, x0, sigma, offset):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))+offset

def fit_gaussians(xl,yl,wave,spectrum,lw=50,ax=None):
    """Using coordinates of line features (x, y), fit gaussians to each feature
        around 'linewidth' angstroms from feature center
    """

    # turn linewidth into width in pixels
    #xw = (linewidth/np.diff(wave)[0])/2.
    #xw = int(xw)

    # store gaussians
    g = []
    for xpeak,ypeak in zip(xl,yl):
        # slice data around line center
        idx = np.where((wave < xpeak+lw/2) & (wave > xpeak-lw/2))
        xslice = wave[idx]
        yslice = spectrum[idx]

        #plot_spectrum(xslice,yslice,color='m',ls='--',ax=ax)

        try:
            # calculate local continuum
            con = np.nanmean(yslice)
            # set initial guess
            
            p0 = [ypeak-con,xpeak,lw/2,con]  #a,x0,sigma,offset
            popt,pcov = curve_fit(gauss_function,xslice,yslice,p0=p0)
        except:
            # sometimes it breaks because code is jank?
            #   just skip this feature
            continue

        # only accept if the sigma of the gaussian is 'reasonable'?
        if np.abs(popt[2]) < lw:
            g.append(popt)

            if ax:
                plot_spectrum(xslice,gauss_function(xslice,*popt),color='m',ls='--',ax=ax)
    return g


def mask_gaussians(gaussians,x):
    """Mask out 2root2*sig from each gaussian feature
    """
    mask = np.zeros_like(x)
    for g in gaussians:
        x0 = g[1]
        lw = np.abs(2 * g[2] *np.sqrt(2))
        idx = np.where((x < x0+lw) & (x > x0-lw))
        mask[idx] = 1
        
    return mask


def spline_fit(fit_me, xi, xf,order=3,s=1):
    """Spline fit and interpolate
    """
    
    # univariate spline cannot handle masked arrays, so this fixes that?
    weights = np.isnan(fit_me)
    splinefunc = USplineFit(xi,fit_me, k=order,s=s,w=~weights)
    fitted = splinefunc(xf)
    residual = splinefunc(xi) - fit_me
    return (fitted, residual)


def main():
    parser = argparse.ArgumentParser(description="Try doing smoothing things to flux calibrate a star?")
    parser.add_argument('spectrum',type=str,help="Input spectrum FITS file")
    parser.add_argument('-k',metavar='kernel',type=float,default=10,help='Specify kernel for initial Gaussian smoothing (default=10)')
    parser.add_argument('-lw',metavar='linewidth',type=float,default=50,help='Specify approximate linewidth of the larger absorption features in Angstroms (default=50)')

    args = parser.parse_args()

    # read in spectrum
    header,wave,spectrum = get_spectrum(args.spectrum)

    # gently smooth first because reasons?
    smoothed = smooth(spectrum,kernel=args.k)

    # plot original
    ax = plot_spectrum(wave,spectrum,color='k')

    # overplot smoothed
    plot_spectrum(wave,smoothed,ax=ax,color='b',ls='--')

    # find local minima
    xl,yl = find_lines(smoothed,x_axis=wave,lookahead=args.lw)

    # plot features
    plot_spectrum(xl,yl,color='m',ls='o',ax=ax)

    # fit gaussians to each found feature
    #  basically, we just want the width of the line to excise it
    #  from the spectrum
    gaussians = fit_gaussians(xl,yl,wave,smoothed,args.lw,ax=ax)

    # excise gaussians from spectrum
    mask = mask_gaussians(gaussians,wave)

    # mask out gaussians
    waveM = np.ma.array(wave,mask=mask,fill_value=np.nan)
    specM = np.ma.array(smoothed,mask=mask,fill_value=np.nan)
    #plot_spectrum(waveM,specM,color='r',ax=ax)

    # spline fit to smooth
    #  re-interpolate back to original wave
    specS,_ = spline_fit(specM[~specM.mask],waveM[~waveM.mask],wave)

    # finally, smooth again cuz why not?
    specF = smooth(specS,kernel=args.k)
    
    plot_spectrum(wave,specF,color='r',ax=ax)
    
    plt.show()
    
    

if __name__ == '__main__':
    main()
