#! /usr/bin/env python
import argparse
import pyfits
import numpy as np
import matplotlib.pyplot as plt
from target_utils import apertures_from_region

def head_append(header):
    new=header
    new['CTYPE1']='LINEAR'
    new['CTYPE2']='LINEAR'
    new['CDELT1']=1
    new['CDELT2']=1
    new['CD1_1']=1
    new['CD2_2']=1
    new['DISPAXIS']=1
    new['CRPIX1']=1
    new['CRVAL1']=1
    return new

def main():
    parser = argparse.ArgumentParser(description='Extracts apertures into 1D spectral cuts.')
    parser.add_argument('ffimg',type=str,help='Flatfielded image file.')
    parser.add_argument('reg',type=str,help='Region file defining apertures.')
    
    args=parser.parse_args()
    
    apertures=apertures_from_region(args.ffimg,args.reg)
    
    aps1D=[]
    for i in apertures:
        aps1D.append(np.median(i,axis=0))
    
    header=pyfits.getheader(args.ffimg)
    new_head=head_append(header)
    
    print 'Writing spectral cuts to NGC253.ms.fits'
    pyfits.writeto('NGC253.ms.fits', aps1D, new_head)


if __name__ == '__main__':
    main()
