#! /usr/bin/env python
import argparse
from pyraf import iraf

def main():
    parser = argparse.ArgumentParser(description='Fixes BITPIX issue with archive data')
    parser.add_argument('filelist',nargs='+',help='Input images to process')

    args = parser.parse_args()

    for image in args.filelist:
        iraf.hedit(images=image,fields='BITPIX',value=32,update=True,show=True,addonly=True)


if __name__ == '__main__':
    main()
