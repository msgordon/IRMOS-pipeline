#! /usr/bin/env python
import pyfits
import numpy as np
import glob

##########
### DataObject
##########
class DataObject:
    # Construct DataObject from filename
    def __init__(self,data,header,normalize=False):
        self.data = data
        self.header = header

        if normalize:
            # Normalize by exptime
            self.data /= np.float(self.header['EXPTIME'])/1000.0 # ms

    def __call__(self,*args):
        return self

    @classmethod
    def fromfilename(cls,filename,normalize=False):
        data,header = pyfits.getdata(filename,0,header=True)
        obj = cls(data,header,normalize=normalize)
        obj.filename = filename
        return obj
        

##########
### DataCube
##########
class DataCube:
    @staticmethod
    # Pull filenum from filename
    def get_filenum(filename,path,source_name,ext):
        filestr = filename.split('_')
        filestr = filestr[-1].strip(ext)
        return int(filestr)
        #return int(filename[len(''.join([path,source_name])):-len(ext)])

    @staticmethod
    # Grab only the files between a range
    def get_filelist(path,source_name,first_frame,last_frame,ext):
        if path[-1] != '/':
            path += '/'
        base = ''.join([path,source_name,'*',ext])
        # Filter if file number between first and last frame
        filelist = []
        for f in glob.glob(base):
            try:
                filenum = DataCube.get_filenum(f,path,source_name,ext)
            except:
                print 'Error in %s' % f
                continue
            if (filenum <= last_frame) and (filenum >= first_frame):
                filelist.append(f)
        filelist.sort()
        return filelist
        
    @classmethod
    def fromfilelist(cls,filelist,normalize=False):
        datalist = []
        for pfile in filelist:
            datalist.append(DataObject.fromfilename(pfile,normalize=normalize))

        cube = cls(datalist)
        cube.filelist = filelist
        return cube
        
        
    # Construct DataCube from list of objects
    def __init__(self,objectlist):
        self.datalist = objectlist
        
    # Return DataObject
    def __getitem__(self,val):
        return self.datalist[val]

    def __len__(self):
        return len(self.datalist)
    
    def __call__(self,*args):
        return self

    def combine(self,method="median"):
        c = None

        if method == "mean":
            c = np.mean([d.data for d in self],axis=0)
        elif method == "median":
            c = np.median([d.data for d in self],axis=0)
        elif method == "sum":
            c = np.sum([d.data for d in self],axis=0)

        return c
