#! /usr/bin/env python
import argparse
import pyfits
import numpy as np
import matplotlib.pyplot as plt
from target_utils import apertures_from_region

def main():
    parser = argparse.ArgumentParser(description='Extracts apertures into 1D spectral cuts.')
    parser.add_argument('ffimg',type=str,help='Flatfielded image file.')
    parser.add_argument('reg',type=str,help='Region file defining apertures.')
    
    args=parser.parse_args()
    
    apertures=apertures_from_region(args.ffimg,args.reg)
    
    #plt.imshow(apertures[0], origin='lower')
    
    aps1D=[]
    for i in apertures:
        aps1D.append(np.median(i,axis=0))


if __name__ == '__main__':
    main()
