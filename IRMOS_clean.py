#! /usr/bin/env python
import pyfits
import LAcosmics
import argparse
import os.path


def main():
    parser = argparse.ArgumentParser(description='LACosmics cleaning on input files.')

    parser.add_argument('file',nargs='+',help='Input file(s)')
    parser.add_argument('-o',type=str,metavar='outdir',help='Optional output directory. If not specified, input files will be overwritten')

    args = parser.parse_args()

    for f in args.file:
        raw = pyfits.open(f)
        raw[0].header['LACosmic'] = (True,'Data cleaned using LACosmic')

        print 'Cleaning %s ...' % f

        clean = LAcosmics.clean_data(raw[0].data)

        if args.o:
            outfile = os.path.basename(f)
            outfile = os.path.join(args.o,outfile)
            raw[0].header['drname'] = (f,'Unclean original')
        else:
            outfile = f

        print 'Writing to %s' % outfile
        raw[0].header['name'] = outfile
        pyfits.writeto(outfile,clean,header=raw[0].header,clobber=True)
    


if __name__ == '__main__':
    main()
