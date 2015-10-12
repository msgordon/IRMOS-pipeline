#! /usr/bin/env python
import argparse
from rotate import Rotator
import pyfits
from scipy.ndimage.interpolation import rotate
import os.path



def main():
    parser = argparse.ArgumentParser(description='Detect angle of spectra and derotate images.')
    #parser.add_argument('ref',type=str,help='Reference image for rotation (usually flat field image)')
    parser.add_argument('filelist',nargs='+',help='Images to be rotated')
    parser.add_argument('-angle',type=float,default=-1.15,help='If specified, disable automatic angle detection and just apply this rotation. [HARDCODED TO BE -1.15 degrees]')
    parser.add_argument('-o',metavar='outdir',type=str,help='Specify directory to write out files (default is same as input')
    parser.add_argument('--c',action='store_true',help='If specified, clobber images on output')
    #parser.add_argument('--sigma',type=float,default=50,help='Sigma value for detection regression (default=50)')
    #parser.add_argument('--threshold',type=float,default=0.8,help='Detection threshold for regression (default=0.8)')

    args = parser.parse_args()

    ###  !!! ANGLE WAS DETERMINED TO BE -1.15 degrees in all cases
    ###args.angle=-1.15
    print 'Rotating images by %.2f degrees' % args.angle
    
    for infile in args.filelist:
        print '\tRotating %s' % infile
        hdu = pyfits.open(infile)
        rotated = rotate(hdu[0].data,args.angle)
        hdu[0].header['ANGLE'] = (args.angle,'Rotation angle')

        if args.o:
            outdir = args.o
        else:
            outdir = os.path.dirname(infile)

        outfile = os.path.splitext(os.path.basename(infile))
        outfile = ''.join([outfile[0],'.r',outfile[1]])
        outfile = os.path.join(outdir,outfile)

        hdu[0].header['REF'] = (infile,'Filename before rotation')
        hdu[0].header['NAME'] = outfile
        print '\tWriting to %s' % outfile
        print
        pyfits.writeto(outfile,rotated,hdu[0].header,clobber=args.c)
            
    
    #ref = pyfits.getdata(args.ref)
    #print 'Rotating reference image: %s' % args.ref
    #ref_cr = Rotator(ref,sigma=args.sigma,threshold=args.threshold)
    #ref_cr.run(angle=args.angle)
    #ref_cr.display()
    



if __name__ == '__main__':
    main()
