#! /usr/bin/env python
import numpy as np
import pyfits

def targets_from_region(filename):
    '''Read target stripes from region file.'''

    targets = []
    with open(filename, 'r') as f:
        for line in f:
            if line.split('(')[0] != 'line':
                continue

            line = line.split(',')
            targets.append(line[1])

        
    targets = np.array(targets).astype(float).astype(int)
    targets_t = []
    for i in np.arange(1,len(targets),2):
        targets_t.append((targets[i-1],targets[i]))
        
    return targets_t


def apertures_from_region(data, regfile):
    '''Return aperture slices from data.'''
    if isinstance(data,str):
        data = pyfits.getdata(data)

    targets = targets_from_region(regfile)

    apertures = []
    for target in targets:
        aperture = data[target[1]:target[0],:]
        apertures.append(aperture)

    return apertures
