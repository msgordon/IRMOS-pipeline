#! /usr/bin/env python
import argparse
from IRMOS_reader import DataCube
import pyfits


def main():
    parser = argparse.ArgumentParser(description='Read and combine images from IRMOS archive')
    parser.add_argument('dir',type=str,help='Directory name of target images.')
    parser.add_argument('basename',type=str,help='Basename of target files before file number. Ex: for "OMC1_South_6.fit" specify "OMC1_South_"')
    parser.add_argument('filerange',type=int,nargs=2,help='First and last filenumber in series to combine')
    parser.add_argument('outfile',type=str,help='Output filename')
    parser.add_argument('-method',choices=('mean','median','sum'),default='median',help='Specify method of combining images (default="median")')
    parser.add_argument('-ext',type=str,default='.fit',help='Filename extension (default=".fit")')

    args = parser.parse_args()

    
    print 'Reading from %s/%s*%s...' % (args.dir,args.basename,args.ext)
    
    SOURCE_list = DataCube.get_filelist(args.dir,args.basename,args.filerange[0],args.filerange[1],args.ext)

    for source in SOURCE_list:
        print '\t%s'%source

    print '\nNormalizing and combining images, method=%s' % args.method
    SOURCE_dc = DataCube.fromfilelist(SOURCE_list, normalize=True)
    SOURCE_med = SOURCE_dc.combine(method=args.method)
    
    print 'Updating header'
    header = SOURCE_dc[0].header
    header['NAME'] = args.outfile
    header['BASEDIR'] = (args.dir,'Path of input images')
    header['BASENAME'] = (args.basename, 'Basename of input images')
    header['NUM_STRT'] = (args.filerange[0],'Start of filelist')
    header['NUM_END'] = (args.filerange[1],'End of filelist')
    header['NUM_COMB'] = (len(SOURCE_list),'Number of files combined')
    header['COMBINE'] = (args.method,'Combine method')
    header['NORM'] = (True,'Normalized by exptime')
    
    print 'Writing to %s' % args.outfile
    pyfits.writeto(args.outfile,SOURCE_med,header=header,clobber=True)
    

if __name__ == '__main__':
    main()
