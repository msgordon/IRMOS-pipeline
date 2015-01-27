#! /usr/bin/env python
import argparse
import pyfits
import ConfigParser

def Header(config,header,section):
    head=header
    head['CDELT1']=config.getfloat(section,'crdelt1')
    head['CRPIX1']=config.getint(section,'crpix1')
    head['CRVAL1']=config.getfloat(section,'crval1')
    return head

def main():
    parser = argparse.ArgumentParser(description='Writes a file for every aperture with the calibrated header info.')
    parser.add_argument('specimg',type=str,help='Image file for the 1D spectra cuts.')
    parser.add_argument('cal',type=str,help='File containing calibration info.')
    parser.add_argument('name',type=str,help='Name of data set (e.g. NGC253).')
    
    args=parser.parse_args()
    
    data=pyfits.getdata(args.specimg)
    header=pyfits.getheader(args.specimg)
    config=ConfigParser.ConfigParser()
    config.read(args.cal)
    
    print "Writing spectra files to new folder."
    
    for idx,row in enumerate(data):
        pyfits.writeto('%s_spectra/%s_spec%i.fits' % (args.name, args.name, idx), row, Header(config,header,'%s.ms_%i' % (args.name, len(data)-idx-1)))

if __name__ == '__main__':
    main()
