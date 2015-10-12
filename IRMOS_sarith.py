#! /usr/bin/env python
import argparse
import pyfits
import numpy as np
from scipy.interpolate import interp1d
import sys


def getwaves(header, n):
    cdelt = header['CDELT1']
    crval = header['CRVAL1']

    x = np.arange(0,n)*cdelt + crval
    return x

def rescale(x,y,minwave,maxwave):
    # newx same length as original spectrum, but rescaled
    newx = np.linspace(minwave,maxwave,num = len(x))

    fy = interp1d(x,y, kind='slinear',bounds_error=False)

    #apply interp function to newx
    newy = fy(newx)

    return (newx,newy)

def getoperation(op):
    if op == '+':
        return np.add
    if op == '-':
        return np.subtract
    if op == '*':
        return np.multiply
    if op == '/':
        return np.divide
    if op == 'mean':
        return np.add
    
def operate(func,op1,op2):
    return func(op1,op2)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(description='Performs spectra arithmetic on input files')
    parser.add_argument('input1',help='Operand 1. Must be spectrum file')
    parser.add_argument('op',choices=('+','-','*','/','mean'),help='Operation to perform')
    parser.add_argument('input2',type=str,help='Operand 2.  May be spectrum file or constant.')
    parser.add_argument('out',type=str,help='Output file')
    parser.add_argument('--c',action='store_true',help='If specified, overwrite')

    args = parser.parse_args()

    op1y,op1h = pyfits.getdata(args.input1,header=True)
    op1x = getwaves(op1h,len(op1y))
    
    if is_number(args.input2):
        # perform arithmetic
        op2 = np.float(args.input2)

        # if mean selected with input2 as constant, exit
        if args.op == 'mean':
            sys.exit('Error: Cannot mean combine with constant.')

        op = getoperation(args.op)
        opY = operate(op, op1y, op2)

        hdr = op1h
        hdr['OP1'] = args.input1
        hdr['OP2'] = args.input2
        hdr['OP'] = args.op
        hdr['NAME'] = args.out
        
        print 'Performing scalar arithmetic on %s' % args.input1
        print 'Writing %s' % args.out
        pyfits.writeto(args.out,opY,header=hdr,clobber=args.c)
        

    else:
        # perform spectrum arithmetic
        op2y,op2h = pyfits.getdata(args.input2,header=True)
        op2x = getwaves(op2h,len(op2y))

        # rescale
        min_wave = np.min([np.min(op1x),np.min(op2x)])
        max_wave = np.max([np.max(op1x),np.max(op2x)])
        print 'Rescaling spectra'
        op1x,op1y = rescale(op1x,op1y,min_wave,max_wave)
        op2x,op2y = rescale(op2x,op2y,min_wave,max_wave)

        op = getoperation(args.op)
        opY = operate(op, op1y, op2y)

        if args.op == 'mean':
            opY /= 2.0

        hdr = op1h
        hdr['OP1'] = args.input1
        hdr['OP2'] = args.input2
        hdr['OP'] = args.op
        hdr['CDELT1'] = np.diff(op1x)[0]
        hdr['CRVAL1'] = np.min(op1x)
        hdr['NAME'] = args.out
        
        print 'w0: %.2f, w1: %.2f, dw: %.2f' % (min_wave,max_wave,hdr['CDELT1'])
        print 'Writing %s' % args.out
        
        pyfits.writeto(args.out,opY,header=hdr,clobber=args.c)

    
if __name__ == '__main__':
    main()
