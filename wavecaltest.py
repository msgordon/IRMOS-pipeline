#! /usr/bin/env python

import pyfits
import numpy as np

data=pyfits.getdata('NGC253.ms.fits')
aperture=data[0]
header=pyfits.getheader('NGC253.ms.fits')

x=np.array([280,307,336,344,352,369,387,473,505,522,541,562])
y=np.array([19771.8,20008.2,20275.9,20339.5,20412.7,20563.6,20729,21505.5,21802.2,21955.6,22125.5,22312.7])

z=np.polyfit(x,y,1)
p=np.poly1d(z)

header['CDELT1']=z[0]
header['CRPIX1']=1
header['CRVAL1']=p(1)

print 'Writing .fits file for the spectrum'
pyfits.writeto('NGC253_s1.fits', aperture, header)
