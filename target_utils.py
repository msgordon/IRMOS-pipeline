#! /usr/bin/env python
import numpy as np

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
