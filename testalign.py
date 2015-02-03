#! /usr/bin/env python
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pyfits

def get_spectrum(filename):
    data, header = pyfits.getdata(filename, header=True)

    # check if 1D
    if len(data) != int(header['NAXIS1']):
        data = data[0]

    minwave = header['CRVAL1']
    maxwave = len(data)*header['CDELT1']+minwave
    waves = np.linspace(minwave, maxwave, num=len(data))

    return (waves, data)
    

def main():
    parser = argparse.ArgumentParser(description='Aligns input spectra')
    parser.add_argument('filelist',nargs='+',help='List of input spectra')
    
    args = parser.parse_args()

    plt.figure()

    spectra = [get_spectrum(filename) for filename in args.filelist]

    for idx, spectrum in enumerate(spectra):
        waves, data = spectrum
        plt.plot(waves,data+idx)

    min_wave = np.max([np.min(x[0]) for x in spectra])
    max_wave = np.min([np.max(x[0]) for x in spectra])

    plt.vlines([min_wave, max_wave], 0, len(spectra), linewidth=5)
    
    plt.show()

if __name__ == '__main__':
    main()
