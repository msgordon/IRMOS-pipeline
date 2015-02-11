#! /usr/bin/env python
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pyfits
from scipy.interpolate import interp1d

def get_spectrum(filename):
    data, header = pyfits.getdata(filename, header=True)

    # check if 1D
    if len(data) != int(header['NAXIS1']):
        data = data[0]

    start = header['CRVAL1']
    step = header['CDELT1']
    waves = np.arange(0,len(data))*step+start
    #waves = np.linspace(minwave, maxwave, num=len(data))

    return (waves, data)

def rescale(spectrum,minwave,maxwave):
    # newx same length as originally spectrum, but rescaled
    newx = np.linspace(minwave,maxwave,num = len(spectrum[0]))

    fy = interp1d(spectrum[0],spectrum[1], kind='linear',bounds_error=False)

    #apply interp function to newx

    newy = fy(newx)

    return (newx,newy)


def combine_sky(spectra):
    ys = np.array([spec[1] for spec in spectra])
    y = np.nanmean(ys,axis=0)

    #all xs are the same, so choose the first
    return (spectra[0][0], y)
    

def main():
    parser = argparse.ArgumentParser(description='Aligns input spectra')
    parser.add_argument('filelist',nargs='+',help='List of input spectra')
    
    args = parser.parse_args()

    plt.figure()

    spectra = [get_spectrum(filename) for filename in args.filelist]

    ## plot all together and offset to test alignment
    for idx, spectrum in enumerate(spectra):
        waves, data = spectrum
        plt.plot(waves,data+idx)

    #find bounds
    min_wave = np.min([np.min(x[0]) for x in spectra])
    max_wave = np.max([np.max(x[0]) for x in spectra])

    # plot bounds
    #plt.vlines([min_wave, max_wave], 0, len(spectra), linewidth=5)
    
    newspectra = [rescale(spec,min_wave,max_wave) for spec in spectra]

    # newspectra should all be same length, same waves
    skyspec = combine_sky(newspectra)

    plt.figure()
    plt.plot(skyspec[0],skyspec[1])
    
    plt.show()

if __name__ == '__main__':
    main()
