#! /usr/bin/env python
import argparse
import pyfits
import numpy as np
import os.path

def is_normalized(data, header, key, normkey):
    if normkey in header:
        pass
    else:
        header[normkey]=False
    if header[normkey]==True:
        return True
    else:
        return False
    '''
    Return true if keyword 'normkey' is true in header
    '''

    
def normalize(data, header, key, normkey):
    expsec=int(header[key])/1000
    for i,j in enumerate(data):
        data[i]=j/expsec
    header[normkey]=True
    '''
    Divide image by exposure time keyword "key"
    Update keyword "normkey" to True
    '''
    return data, header
    


def main():
    parser = argparse.ArgumentParser(description='Normalize image by exptime. If image already normalized, it is skipped.')
    parser.add_argument('filelist', nargs='+', help='Files to normalize')
    parser.add_argument('-o',metavar='outdir', type=str, help='Specify optional output directory, otherwise rewrite file')
    parser.add_argument('-key', type=str, default='EXPTIME', help='Specify exposure time keyword (default=EXPTIME)')
    parser.add_argument('-normkey',type=str, default='NORM', help='Specify normalized keyword (default=NORM)')
    parser.add_argument('--c',action='store_true',help='If specified, force clobber on write')

    args = parser.parse_args()

    for filename in args.filelist:
        data,header = pyfits.getdata(filename, header=True)

        # If already normalized, skip this file
        if is_normalized(data, header, args.key, args.normkey)==True:
            print 'Skipping %s.  Already normalized.' % filename
            continue

        # Else, normalize
        data, header = normalize(data, header, args.key, args.normkey)

        if args.o:
            outname = os.path.join(args.o, filename)
        else:
            outname = filename

        print 'Writing to %s' % outname
        pyfits.writeto(outname, data, header=header, clobber=args.c)
            

if __name__ == '__main__':
    main()
