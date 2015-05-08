#! /usr/bin/env python
import argparse
import numpy as np
import pyfits
from math import sqrt

parser = argparse.ArgumentParser(description='Checks signal-to-noise ratio for a given peak in a spectrum.')
parser.add_argument('specimg',type=str,help='Spectrum file.')
parser.add_argument('bglow',nargs=2,type=int,help='Background range before the peak in Angstroms (Enter 2 numbers, low and high).')
parser.add_argument('peak',nargs=2,type=int,help='Peak range in Angstroms (Enter 2 numbers, low and high).')
parser.add_argument('bghigh',nargs=2,type=int,help='Background range after the peak in Angstroms (Enter 2 numbers, low and high).')
args=parser.parse_args()

ydata=pyfits.getdata(args.specimg)
head=pyfits.getheader(args.specimg)
xmin=head['CRVAL1']
xmax=len(ydata)*head['CDELT1']+head['CRVAL1']
xdata=np.arange(xmin,xmax,head['CDELT1'])

yvals=np.array([ydata[i] for i,j in enumerate(xdata) if j>=args.peak[0] and j<=args.peak[1]])
signal=np.trapz(yvals,dx=head['CDELT1'])

lowvals=np.array([ydata[i] for i,j in enumerate(xdata) if j>=args.bglow[0] and j<=args.bglow[1]])
lowrms=sqrt(sum(n*n for n in lowvals)/float(len(lowvals)))
highvals=np.array([ydata[i] for i,j in enumerate(xdata) if j>=args.bghigh[0] and j<=args.bghigh[1]])
highrms=sqrt(sum(n*n for n in highvals)/float(len(highvals)))
noise=(lowrms+highrms)/2.0

SN=signal/noise

print 'Signal/Noise is: %f' % SN
