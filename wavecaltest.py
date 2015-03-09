#! /usr/bin/env python

import pyfits
import numpy as np
import matplotlib.pyplot as plt

'''data=pyfits.getdata('NGC253.ms.fits')
aperture=data[0]
header=pyfits.getheader('NGC253.ms.fits')'''

x=np.array([221,247,275,290,308,325,442,459,477,498])
y=np.array([19771.80,20008.20,20275.90,20412.70,20563.60,20729.00,21802.20,21955.60,22125.50,22312.70])

z=np.polyfit(x,y,1)
p=np.poly1d(z)

'''header['CDELT1']=z[0]
header['CRPIX1']=1
header['CRVAL1']=p(1)'''

#xfit=np.arange(np.min(x),np.max(x)+200,1)
#c=np.polynomial.legendre.legfit(x,y,3)
#yfit=np.polynomial.legendre.legval(xfit,c)
xfit=np.arange(np.min(x),np.max(x),1)
yfit=np.array(p(xfit))

plt.plot(x,y,'bs')
plt.plot(xfit,yfit,'r-')
plt.show()

'''print 'Writing .fits file for the spectrum'
pyfits.writeto('NGC253_s1.fits', aperture, header)'''
