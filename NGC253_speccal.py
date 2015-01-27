#! /usr/bin/env python
import pyfits
import ConfigParser

def Header(header,section):
    head=header
    head['CDELT1']=config.getfloat(section,'crdelt1')
    head['CRPIX1']=config.getint(section,'crpix1')
    head['CRVAL1']=config.getfloat(section,'crval1')
    return head

data=pyfits.getdata('NGC253.ms.fits')
config=ConfigParser.ConfigParser()
config.read('database/NGC253.ms.cal')
header=pyfits.getheader('NGC253.ms.fits')


print "Writing spectra files to NGC253_spectra."

for idx,row in enumerate(data):
    pyfits.writeto('NGC253_spectra/NGC253_spec%i.fits' % idx, row, Header(header,'NGC253.ms_%i' % len(data)-idx-1))
