import numpy as np
import matplotlib.pyplot as plt
from skimage import measure,filter
#import ds9
import pyfits
from scipy.ndimage.interpolation import rotate
from scipy.stats import linregress

class Rotator:

    def __cal__(self,*args):
        return self

    # Construct Rotator from data and gaussian sigma
    def __init__(self,data,sigma=15,threshold=0.8,header=None):
        self.data = data.astype(np.float)
        self.sigma = sigma
        self.threshold = threshold
        self.edges = None
        self.contours = None
        self.slopes = None
        self.slope = None
        self.angle = None
        self.rotated = data
        self.header = header  # Just in case
        self.regions = None

    def find_edges(self,sigma=None):
        if sigma is not None:
            self.sigma = sigma

        print 'Identifying edges...'
        self.edges = filter.canny(self.data,sigma=self.sigma)
        return self.edges

    def find_contours(self,threshold=None):
        if threshold is not None:
            self.threshold = threshold

        if self.edges is None:
            self.edges = self.find_edges()

        print 'Finding contours...'
        self.contours = measure.find_contours(self.edges,self.threshold,fully_connected='high')
        return self.contours

    def regression(self):
        if self.contours is None:
            self.contours = self.find_contours()

        print 'Calculating regression line...'
        self.slopes = []
        self.intercepts = []
        for contour in self.contours:
            slope, intercept, r_value, p_value, std_err = linregress(contour[:,1],contour[:,0])
            # Cut on contours
            if (np.isfinite(slope) and slope != 0.0 and intercept < self.data.shape[0] and intercept > 0):
                self.slopes.append(slope)
                self.intercepts.append(intercept)

        #self.slopes = np.array(self.slopes)
        #self.slopes = self.slopes[np.isfinite(self.slopes)]
        #self.slopes = self.slopes[np.where(self.slopes != 0.0)[0]]

        self.slope = np.median(self.slopes)
        return self.slope

    def find_angle(self):
        if self.slope is None:
            self.slope = self.regression()

        print 'Computing angle of correction...'
        self.angle = np.arctan(self.slope)*180.0/np.pi
        return self.angle

    def rotate(self,angle=0,transpose=False):
        print 'Rotating data by %f degrees...' % angle
        self.rotated = rotate(self.data,angle)
        if transpose:
            self.rotated = self.rotated.transpose()

        return self.rotated

    def run(self,sigma=None,threshold=None,transpose=False,angle=False):
        if sigma is not None:
            self.sigma = sigma
        if threshold is not None:
            self.threshold = threshold
        self.find_edges(sigma=self.sigma)
        self.find_contours(threshold=self.threshold)
        self.regression()
        if angle is False:
            angle = self.find_angle()
        self.angle=angle
        self.rotate(angle=angle,transpose=transpose)

        return self.rotated
        
    def display(self):#,plotDS9=False,plotPLT=False,plotAll=True,show=True):
        '''
        if (plotAll or plotDS9) and not plotPLT:
            d = ds9.ds9()
            d.set("frame 1")
            print self.data.dtype
            d.set_np2arr(self.data,dtype=float)
            if self.edges is not None:
                d.set("frame 2")
                d.set_np2arr(self.edges,dtype=int)
            if self.rotated is not None:
                d.set("frame 3")
                d.set_np2arr(self.rotated,dtype=float)
       
        if (plotPLT or plotAll) and (not plotDS9) and (self.contours is not None):
            for n,contour in enumerate(self.contours):
                plt.plot(contour[:,1], contour[:,0])
           
            if show:
                plt.show()
        #'''
        plt.figure()
        plt.imshow(self.data,origin='lower',cmap='gray_r')
        plt.title('Original')
        for n,contour in enumerate(self.contours):
            plt.plot(contour[:,1], contour[:,0])

        plt.figure()
        plt.imshow(self.edges,origin='lower',cmap='gray_r')
        plt.title('Edges')
        
        plt.figure()
        plt.imshow(self.rotated,origin='lower',cmap='gray_r')
        plt.title('Rotated')
        plt.show()
        return

    def targets(self):
        targets = []
        for i in xrange(0,len(self.contours)-1):
            targets.append((self.contours[i][0,1],self.contours[i+1][0,1]))
        return targets
            
    def make_regions(self,filename,transpose=False):
        header = '''# Region file format: DS9 version 4.1\n# Filename:\nglobal color=green dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\nphysical'''

        '''
        f = open(filename,'w')
        print 'Writing regions to %s...' % filename
        ## Get two points on line  (center x, y) (0,b)
        for m,b in zip(self.slopes,self.intercepts):
            #xc = data.shape[0]/2
            #calculate y at center x
            #yc = m*xc + b
            xp = -b*np.sin(self.angle)
            yp =  b*np.cos(self.angle)
            if transpose:
                f.write('line(%f,%f,%f,%f)\n' % (
                
        '''
        '''
        self.regions = filename
        f = open(filename,'w')
        print 'Writing regions to %s...' % filename
        if transpose:
            for x in self.intercepts:
                f.write('vector(%f,%f,%f,%f)\n' % (x,0,self.data.shape[0],90))
        else:
            for y in self.intercepts:
                f.write('vector(%f,%f,%f,%f)\n' % (0,y,self.data.shape[0],0))

        f.close()
        '''

        self.regions = filename
        f = open(filename,'w')
        print 'Writing regions to %s...' % filename
        length = self.data.shape[0]
        angle = 90
        for idx,contour in enumerate(self.contours):
            f.write('vector(%f,%f,%f,%f) # text = "%i"\n' % (contour[0,1],0,length,angle,idx))
        return

    @staticmethod
    def targets_from_region(filename):
        f = open(filename,'r')
        targets = []
        for line in f:
            line = line.split(',')
            line[0] = line[0].split('(')
            targets.append(line[0][1])
        f.close()

        targets = np.array(targets).astype(float).astype(int)
        targets_t = []
        for i in np.arange(1,len(targets),2):
            targets_t.append((targets[i-1],targets[i]))
        return targets_t
    
