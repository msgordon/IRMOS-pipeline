#! /usr/bin/env python
import argparse
import pyfits
import numpy as np
import os.path

def is_normalized(header, normkey):
    '''
    Return true if keyword 'normkey' is true in header
    '''
    if normkey in header and header[normkey]:
        return True
    else:
        return False

    
def normalize(data, header, key, normkey):
    '''
    Divide image by exposure time keyword "key"
    Update keyword "normkey" to True
    '''
    exptime = np.float(header[key])/1000.
    data /= exptime
    header[normkey] = (True, 'Data is normalized')
    
    return data, header
    


def main():
    parser = argparse.ArgumentParser(description='Normalize image by exptime. If image already normalized, it is skipped.')
    parser.add_argument('filelist', nargs='+', help='Files to normalize')
    parser.add_argument('-o',metavar='outfile', type=str, help='Specify optional output file, otherwise rewrite file')
    parser.add_argument('-key', type=str, default='EXPTIME', help='Specify exposure time keyword (default=EXPTIME)')
    parser.add_argument('-normkey',type=str, default='NORM', help='Specify normalized keyword (default=NORM)')
    parser.add_argument('--c',action='store_true',help='If specified, force clobber on write')

    args = parser.parse_args()

    for filename in args.filelist:
        data,header = pyfits.getdata(filename, header=True)

        # If already normalized, skip this file
        if is_normalized(header, args.normkey):
            print 'Skipping %s.  Already normalized.' % filename
            continue

        # Else, normalize
        data, header = normalize(data, header, args.key, args.normkey)

        if args.o:
            outname = args.o
        else:
            outname = filename

        print 'Writing to %s' % outname
        pyfits.writeto(outname, data, header=header, clobber=args.c)
            

if __name__ == '__main__':
    main()
