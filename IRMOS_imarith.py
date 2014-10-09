#! /usr/bin/env python
import argparse
import pyfits

def main():
    parser = argparse.ArgumentParser(description='Performs image arithmetic on input files')
    parser.add_argument('op1',type=str,help='Image file, operand 1')
    parser.add_argument('op2',type=str,help='Image file, operand 2')
    parser.add_argument('out',type=str,help='Output file')
    parser.add_argument('-method',choices=('add','sub','mult','div'),default='sub',help='Operation (default="sub")')

    
    args = parser.parse_args()

    op1 = pyfits.open(args.op1)
    op2 = pyfits.open(args.op2)

    header = op1[0].header

    if args.method == 'add':
        print 'Adding input images'
        data = op1[0].data + op2[0].data
    elif args.method == 'sub':
        print 'Subtracting input images'
        data = op1[0].data - op2[0].data
    elif args.method == 'mult':
        print 'Multiplying input images'
        data = op1[0].data * op2[0].data
    elif args.method == 'div':
        print 'Dividing input images'
        data = op1[0].data / op2[0].data

    header['OP1'] = (args.op1,'Operand1')
    header['OPER'] = (args.method,'Operation performed')
    header['OP2'] = (args.op2,'Operand2')
    header['NAME'] = args.out

    pyfits.writeto(args.out,data,header=header,clobber=True)

    
if __name__ == '__main__':
    main()
