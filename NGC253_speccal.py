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


print "Writing spectra files to NGC253_spectra"

#Why not write a 'for' loop...?
for idx,row in enumerate(data):
    pyfits.writeto('folder/NGC253_spec%i.fits' % idx, row, Header(header,'NGC253.ms_%i' % len(data)-idx))
    

pyfits.writeto('NGC253_spectra/NGC253_spec0.fits', data[0], Header(header,'NGC253.ms_15'))
pyfits.writeto('NGC253_spectra/NGC253_spec1.fits', data[1], Header(header,'NGC253.ms_14'))
pyfits.writeto('NGC253_spectra/NGC253_spec2.fits', data[2], Header(header,'NGC253.ms_13'))
pyfits.writeto('NGC253_spectra/NGC253_spec3.fits', data[3], Header(header,'NGC253.ms_12'))
pyfits.writeto('NGC253_spectra/NGC253_spec4.fits', data[4], Header(header,'NGC253.ms_11'))
pyfits.writeto('NGC253_spectra/NGC253_spec5.fits', data[5], Header(header,'NGC253.ms_10'))
pyfits.writeto('NGC253_spectra/NGC253_spec6.fits', data[6], Header(header,'NGC253.ms_9'))
pyfits.writeto('NGC253_spectra/NGC253_spec7.fits', data[7], Header(header,'NGC253.ms_8'))
pyfits.writeto('NGC253_spectra/NGC253_spec8.fits', data[8], Header(header,'NGC253.ms_7'))
pyfits.writeto('NGC253_spectra/NGC253_spec9.fits', data[9], Header(header,'NGC253.ms_6'))
pyfits.writeto('NGC253_spectra/NGC253_spec10.fits', data[10], Header(header,'NGC253.ms_5'))
pyfits.writeto('NGC253_spectra/NGC253_spec11.fits', data[11], Header(header,'NGC253.ms_4'))
pyfits.writeto('NGC253_spectra/NGC253_spec12.fits', data[12], Header(header,'NGC253.ms_3'))
pyfits.writeto('NGC253_spectra/NGC253_spec13.fits', data[13], Header(header,'NGC253.ms_2'))
pyfits.writeto('NGC253_spectra/NGC253_spec14.fits', data[14], Header(header,'NGC253.ms_1'))
pyfits.writeto('NGC253_spectra/NGC253_spec15.fits', data[15], Header(header,'NGC253.ms_0'))
