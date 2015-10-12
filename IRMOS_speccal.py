#! /usr/bin/env python
import os
import argparse
import pyfits
import ConfigParser

def Header(config,header,section,idx):
    head=header
    head['CDELT1']=config.getfloat(section,'crdelt1')
    head['CRPIX1']=config.getint(section,'crpix1')
    head['CRVAL1']=config.getfloat(section,'crval1')
    head['APID']=idx
    return head

def main():
    parser = argparse.ArgumentParser(description='Writes a file for every aperture with the calibrated header info.')
    parser.add_argument('specimg',type=str,help='Image file for the 1D spectra cuts.')
    parser.add_argument('cal',type=str,help='File containing calibration info.')
    parser.add_argument('outdir',type=str,help='Name of data set output directory.')
    
    args=parser.parse_args()
    
    data=pyfits.getdata(args.specimg)
    header=pyfits.getheader(args.specimg)
    config=ConfigParser.ConfigParser()
    config.read(args.cal)
    
    print "Writing spectra files to folder."
    
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    
    for idx,row in enumerate(data):
        section = '%s_%i' % (os.path.splitext(args.specimg)[0], idx)
        print 'Reading section [%s]' % section
        if not config.has_section(section):
            print '\tSection %i not found. Skipping.' % idx

        else:
            outfile = '%s.%i.fits' % (args.specimg.split('.ms.')[0] , idx)
            outfile = os.path.join(args.outdir,outfile)
            hdr = Header(config,header,section,idx)
            print 'Writing %s' % outfile            
            pyfits.writeto(outfile, row, hdr, clobber=True)
            

if __name__ == '__main__':
    main()
