#! /usr/bin/env python
import argparse
import matplotlib.pyplot as plt
import matplotlib.patheffects as PE
import numpy as np
import pyfits
from peakdetect import peakdetect
from scipy.signal import correlate
import os
import ConfigParser


def readlinelist(filename):
    linelist = []
    with open(filename, 'r') as f:
        for line in f:
            if line[0] == '#':
                continue
            line = np.float(line.strip().split()[0])
            linelist.append(line)
    return linelist

def set_featurelist(lines):
    pairs = ['  %i %.2f' %(x[0],x[2]) for x in lines]
    #strlines = 'lines: \n'
    strlines = '\n'.join(pairs)
    return strlines

def get_featurelist(lines):
    pairs = lines.split('\n')
    pairs = [x.split() for x in pairs]
    pairs = [(int(x[0]),float(x[1])) for x in pairs]
    return pairs

def find_peak(data,cm,search,lenx):
    localmax,localmin = peakdetect(data[cm-search:cm+search],x_axis=range(0,lenx)[cm-search:cm+search],lookahead=search/4)
    localmax = sorted(localmax,key=lambda x:x[1])[-1]

    return localmax

def find_shift(ref,data):
    refm = np.ma.array(ref,mask=np.isnan(ref),fill_value=0.)
    datam= np.ma.array(data,mask=np.isnan(data),fill_value=0.)

    corr = correlate(refm.filled(),datam.filled())
    # index of maximum correlation is the amount to shift
    return len(data) - np.argmax(corr)




class Aperture(object):
    def __init__(self,filename,data,aperture,linelist=None,load=False):
        self.filename = filename
        self.linelist = linelist
        self.aperture = aperture
        
        # get database information
        self.databasedir = os.path.join(os.path.dirname(filename),'database')
        self.database = os.path.join(self.databasedir,os.path.splitext(os.path.basename(filename))[0]+'.cal')
        self.section = os.path.basename(self.filename)
        self.section = '%s_%i' % (os.path.splitext(self.section)[0],self.aperture)
        self.orig = data[aperture]
        self.active_data = self.orig
        self.x = range(0,len(self.active_data))
        self.ix = range(0,len(self.active_data))

        # search radius for max pix on each line
        self.search = 10
        self.load = load
        self.lines = []

        # check if done
        self.fitted = False
        
        if load:
            #load from database
            loaded = self._load_lines()
            fitted = self.fit()
            if loaded and fitted:
                self.fitted = True

    def _load_lines(self):
        #read lines from database
        if not os.path.exists(self.database):
            print 'No database file found for %s' % self.filename
            return

        config = ConfigParser.SafeConfigParser()
        print 'Loading calibration from %s' % self.database
        config.read(self.database)
        if not config.has_section(self.section):
            print 'Aperture %i not found in %s' % (self.aperture,self.database)
            return
            

        if not config.has_option(self.section,'lines'):
            print 'Aperture %i calibration not found in %s' % (self.aperture, self.database)
            return

        featurelist = get_featurelist(config.get(self.section,'lines'))
        print 'Loaded %i features for aperture %i' % (len(featurelist),self.aperture)
        ys = [find_peak(self.active_data,x[0],self.search,len(self.x))[1] for x in featurelist]
        self.lines = [[x[0],y,x[1],None] for x,y in zip(featurelist,ys)]
        return self.lines


    def _save_lines(self,m,b,rms,lines):
        #mkdir
        try:
            os.mkdir(self.databasedir)
        except OSError:
            pass #print 'Directory %s exists.' % self.databasedir

        section = self.section

        config = ConfigParser.SafeConfigParser()
        if os.path.exists(self.database):
            config.read(self.database)

        try:
            config.add_section(section)
        except ConfigParser.DuplicateSectionError:
            print 'Overwriting previous calibration'

        featurelist = set_featurelist(lines)
        config.set(section,'CRDELT1','%.3f'%np.abs(m))
        config.set(section,'CRPIX1','1')
        config.set(section,'CRVAL1','%.3f'%b)
        config.set(section,'RMS','%.3f'%rms)
        config.set(section,'lines',featurelist)

        with open(self.database,'w') as configfile:
            print 'Writing aperture %i to %s' % (self.aperture, self.database)
            config.write(configfile)

        return 0

    def fit(self):
        pix = [x[0] for x in self.lines]
        waves = [x[2] for x in self.lines]
        
        if len(waves) < 3:
            print 'At least 3 points required for fitting'
            return

        pairs = zip(pix,waves)
        pairs = sorted(pairs,key = lambda x:x[0])
        #if sorted(waves) != waves:
        #    print 'WARNING: No monotonic solution.  Cannot fit'
        #    return

        p = np.polyfit(pix,waves,1,full=True)
        z = np.poly1d(p[0])
        m = p[0][0]
        # if slope is negative, plot is flipped
        if m < 0:
            b = z(np.max(self.ix))
        else:
            b = z(np.min(self.ix))
        rms = np.sqrt(p[1]/len(pix))
        print 'Slope: %.3f, Ref: %.3f, RMS: %.3f' % (np.abs(m),b,rms)
        self.x = z(self.ix)
        #self.display(self.x,self.active_data,reset=True)
        self.fitted = True
        return (m,b,rms)


    def reidentify(self,reflines,offset):
        guessx = [x[0]+offset for x in reflines]
        try:
            peaks = [find_peak(self.active_data,x,self.search,len(self.x)) for x in guessx]
            # ix, y, s, pid
            newlines = [[peak[0],peak[1],ref[2],None] for peak,ref in zip(peaks,reflines)]
            self.lines = newlines
        except:
            print 'No matching features in aperture %i' % self.aperture
            return None  #failed to find new peaks

        return self.lines

            
    

class Plotter(object):
    def __init__(self, filename, aperture, linelist=None,load=False):
        self.filename = filename
        self.linelist = linelist
        
        self.data = pyfits.getdata(filename)

        # hold all apertures
        self.aps = [None]*len(self.data)
        
        self.ap = Aperture(filename,self.data,aperture,linelist,load)

        self.aps[aperture] = self.ap

        # set reference aperture
        #  if initialized on load, check if actually loaded and set this
        if self.ap.load and self.ap.lines:
            self.iref = aperture
        else:
            self.iref = None
        
        

    def _setup_linelist(self,linelist):
        if isinstance(linelist,str):
            self.linelist = readlinelist(linelist)
        else:
            self.linelist = linelist

        return

    def show(self):
        self._setup_linelist(self.linelist)
        self._setup_subparser()
        self._setup_labeler()
        fig = self._initialize_figure()
        # wait for close
        return 0


    def _setup_labeler(self):
        self.labelmode = False
        self.temppids = []

        # Current position of cursor
        self.ci = None
        return

    def _setup_subparser(self):
        # set up subparser
        self.subparser=argparse.ArgumentParser(description='Parse window text.',prog='')
        self.subparser.add_argument('--r',action='store_true',help='Restore original')
        self.subparser.add_argument('--q',action='store_true',help='Close Plotter and quit')
        self.subparser.add_argument('-w',choices=['a','f'],help="Window functions. 'a' restores axes. 'f' flips x-axis")
        self.subparser.add_argument('--s',nargs='?',default=None,const=-1,help='Save to database.  "--s a" saves all')
        self.subparser.add_argument('--l',action='store_true',help='Load from database')
        self.subparser.add_argument('--setref',nargs='?',type=int,default=None,const=-1,help='Set this aperture (or specified index) as reference.')
        self.subparser.add_argument('--c',nargs='?',default=None,const=-1,help='Calibrate this aperture against reference.  "--c a" calibrates all')
        
        return

    def _initialize_figure(self):
        # initialize figure
        self.fig = plt.figure()
        self.fig.canvas.mpl_disconnect(self.fig.canvas.manager.key_press_handler_id)
        self.keycid = self.fig.canvas.mpl_connect('key_press_event',self.onkey)
        self.motioncid = self.fig.canvas.mpl_connect('motion_notify_event',self.mouse_move)
        self.pid = None

        # Plot initial data
        self.display(self.ap.x,self.ap.active_data,lines=self.ap.lines,reset=True)

        plt.show()
        return self.fig

    def _swap_aperture(self,cap):
        #if aperture already exists, get it
        if self.aps[cap]:
            self.ap = self.aps[cap]
        # load new aperture
        else:
            self.ap = Aperture(self.filename,self.data,cap,self.linelist)
            self.aps[cap] = self.ap

        # Plot initial data
        self.display(self.ap.x,self.ap.active_data,lines=self.ap.lines,reset=True)
        return self.ap

    def _load_all_apertures(self):
        for i in range(0,len(self.data)):
            if self.aps[i]:
                #don't reload if exists
                continue
            else:
                self.aps[i] = Aperture(self.filename,self.data,i,self.linelist)
        return self.aps


    def displaylines(self,lines=None,color='r'):
        arrh = plt.gca().get_ylim()[1]*0.05
        texth = arrh*2
        #print self.lines
        if not lines:
            lines = self.ap.lines

        pids = []
        for line in lines:
            ix,y,s,pid = line  #index of x, y data, string, pid
            line[3] = plt.annotate(s,
                                   xytext=(self.ap.x[ix],y+texth),
                                   xy=(self.ap.x[ix],y+arrh),
                                   rotation=90,va='bottom',ha='center',
                                   arrowprops=dict(arrowstyle="-",color=color),
                                   fontsize=10)
            pids.append(line[3])
        return pids

    def display(self, x, data,lines=None,flip=False,reset=False):
        if plt.gca():
            xlim = plt.gca().get_xlim()
            ylim = plt.gca().get_ylim()

        self.fig.clf()
        
        plt.plot(x,data,lw=1.5,color='k')

        if not reset:
            plt.xlim(xlim)
            plt.ylim(ylim)

        if flip:
            plt.xlim(plt.gca().get_xlim()[::-1])

        self.displaylines(lines)
        self.fig.suptitle('%s[%i]' % (self.ap.filename,self.ap.aperture))
        self.fig.canvas.draw()


    def displaytext(self,text,x=0.05,y=0.05,remove=None):
        if remove:
            remove.remove()
        pid = plt.text(x,y,text,color='k',
                       horizontalalignment='left',
                       verticalalignment='bottom',
                       transform=plt.gca().transAxes)
        #path_effects=[PE.withStroke(linewidth=2,foreground='k')])

        self.fig.canvas.draw()
        return pid

        
        
    def parsetext(self,text):
        args = None
        try:
            # catch -h, or error exit
            args = self.subparser.parse_args(text.split())
        except SystemExit:
            return

        if not args:
            return

        # save features to ./database/
        if args.s == -1:
            fitted = self.ap.fit()
            if fitted:
                m,b,rms = fitted
                self.display(self.ap.x,self.ap.active_data,reset=True)
            else:
                print 'No fit.'
                return
            
            self.ap._save_lines(m,b,rms,self.ap.lines)

            #set this to reference if not already set
            if (self.iref is not None) or (self.iref != 0):
                self.iref = self.ap.aperture
                print 'Aperture %i set as reference' % self.iref
            
            if args.q:
                plt.close()
                return 'Q'
            else:
                return

        # save all to database
        if args.s == 'a':
            for ap in self.aps:
                if not ap:
                    continue
                if ap.lines:
                    print 'Aperture %i, %i lines found' % (ap.aperture,len(ap.lines))
                    fitted = ap.fit()
                    if fitted:
                        m,b,rms = fitted
                        ap._save_lines(m,b,rms,ap.lines)
                    else:
                        print '\tno fit.'
                else:
                    print 'Aperture %i, no lines found' % ap.aperture
            
            self.display(self.ap.x,self.ap.active_data,reset=True)

        if args.c == -1:
            # calibrate this
            self.calibrate(self.ap)

        if args.c == 'a':
            #calibrate all
            if self.iref is None:
                print 'No reference aperture set'
                return
            # preload all aps
            self._load_all_apertures()
            for ap in self.aps:
                self.calibrate(ap,display=False)

        # load features from ./database/
        if args.l:
            lines = self.ap._load_lines()
            if lines:
                self.ap.fit()

            #if loaded and fit, set reference if not already set
            if self.ap.fitted:
                if (self.iref is not None) or (self.iref != 0):
                    self.iref = self.ap.aperture
                    print 'Aperture %i set as reference' % self.iref

            
            self.display(self.ap.x,self.ap.active_data,reset=True)
            return

        # '-wf' flip
        if args.w == 'f':
            self.display(self.ap.x,self.ap.active_data,flip=True)

        # '-wa' restore zoom
        elif args.w == 'a':
            self.display(self.ap.x,self.ap.active_data,reset=True)

        # '--r' restore to default
        if args.r:
            self.ap.active_data = self.ap.orig
            self.ap.x = range(0,len(self.ap.active_data))
            self.ap.ix = range(0,len(self.ap.active_data))
            self.display(self.ap.x,self.ap.active_data,reset=True)


        # set reference file
        if args.setref is not None:
            if args.setref == -1:
                #value not specified, so set this aperture if loaded
                if self.ap.fitted:
                    self.iref = self.ap.aperture
                    print 'Aperture %i set as reference' % self.iref
                else:
                    print 'Must fit aperture %i before it can be used as reference' % self.ap.aperture

            else:
                if self.aps[args.setref].fitted:
                    self.iref = args.setref
                    print 'Aperture %i set as reference' % self.iref
                else:
                    print 'Must fit aperture %i before it can be used as reference' % args.setref

            return

        
        if args.q:
            plt.close()
            return 'Q'

        return

    def pausekey(self,event):
        if not event.key:
            return
            
        elif event.key == 'enter':
            self.fig.canvas.mpl_disconnect(self.keycid)
            self.keycid = self.fig.canvas.mpl_connect('key_press_event',self.onkey)
            if (self.pausetext != '-') and (self.pausetext != self.labeltext):
                
                if not self.labelmode:
                    parsed = self.parsetext(self.pausetext)
                    if parsed == 'Q':
                        return
                    self.pausetext = '-'
                    self.display(self.ap.x,self.ap.active_data)
                    return
                else:
                    #label mode
                    cline = self.pausetext.split(self.labeltext)[1]
                    try:
                        cline = np.float(cline)
                    except:
                        self.pausetext = '-'
                        self.labelmode = False
                        if self.pid:
                            self.pid.remove()
                        for pid in self.temppids:
                            if pid:
                                pid.remove()
                        self.fig.canvas.draw()
                        return
                    #find closest line in list
                    indx = np.searchsorted(self.linelist, [cline])[0]
                    #print indx,len(self.linelist)
                    #print self.linelist[indx]
                    if (indx < len(self.linelist)) and (indx != -1):
                        #if np.abs(self.linelist[indx]-cline) > 1.0:
                        #    s = cline
                        #else:
                        s = self.linelist[indx]
                        ix = self.cm
                        y = self.ap.active_data[ix]
                        self.ap.lines.append([ix,y,s,None])

                    self.pausetext = '-'
                    self.display(self.ap.x,self.ap.active_data)
                    self.labelmode = False
                    return


            else:
                #Clear empty
                self.pausetext = '-'
                self.labelmode = False
                if self.pid:
                    self.pid.remove()
                for pid in self.temppids:                    
                    if pid:
                        pid.remove()
                self.fig.canvas.draw()
                return

        elif (event.key == 'backspace'):
            if self.pausetext == '-':
                return
            if self.pausetext == self.labeltext:
                return
                
            self.pausetext = self.pausetext[0:-1]

        #elif (event.key == None):
        #    return
        #elif (event.key == 'tab'):
        #    print event.key
        elif len(event.key) > 1:
            return
            
        else:
            self.pausetext = ''.join([self.pausetext,event.key])

        self.pid = self.displaytext(self.pausetext,remove=self.pid)
        return


    def onkey(self, event):
        if event.key == '-':
             self.fig.canvas.mpl_disconnect(self.keycid)
             self.pausetext = '-'
             self.labeltext= self.pausetext
             self.pid = self.displaytext(self.pausetext)
             self.keycid = self.fig.canvas.mpl_connect('key_press_event',self.pausekey)
             return

        if event.key == 'm':
            # grab mouse position
            cm = self.ci
            if cm is None:
                return

            localmax = find_peak(self.ap.active_data,cm,self.ap.search,len(self.ap.x))

            self.fig.canvas.mpl_disconnect(self.keycid)
            self.pausetext = '[%i]: ' % localmax[0]
            self.labeltext = self.pausetext
            self.labelmode = True
            self.pid = self.displaytext(self.pausetext)
            self.keycid = self.fig.canvas.mpl_connect('key_press_event',self.pausekey)
            self.cm = localmax[0]
            self.temppids = self.displaylines([[self.cm,localmax[1],'',None]],'b')
            self.fig.canvas.draw()
            return

        #delete line nearby
        if event.key =='d':
            if not self.ap.lines:
                return
            
            # grab mouse position
            cm = self.ci
            if cm is None:
                return

            #find closest line
            #print self.lines
            #print cm

            linexs = np.array([line[0] for line in self.ap.lines])
            #print linexs,cm
            cidx = np.argmin(np.abs(linexs - cm))
            #idx = np.searchsorted(linexs,cm)
            #print idx
            self.ap.lines[cidx][3].remove()
            del self.ap.lines[cidx]
            self.fig.canvas.draw()
            return

        # fit
        if event.key == 'f':
            self.ap.fit()
            self.display(self.ap.x,self.ap.active_data,reset=True)
            
            return

        # if left, get next
        if event.key in ['9','(']:
            cap = self.ap.aperture
            if cap <= 0:
                #at first, so don't get previous
                return

            cap = cap - 1
            self._swap_aperture(cap)
            return

        # if right, get next
        if event.key in ['0',')']:
            cap = self.ap.aperture
            if cap >= (len(self.data)-1):
                #at end, so don't get next
                return

            cap = cap + 1
            self._swap_aperture(cap)
            return

        if event.key == 'c':
            self.calibrate(self.ap)
            return


    def mouse_move(self, event):
        if not event.inaxes:
            self.ci = None
            #self.cx = None
            #self.cy = None
            return

        x, y = event.xdata, event.ydata
        sortx = np.sort(self.ap.x)
        indx = np.searchsorted(sortx, [x])[0]

        # if self.x was reversed, switch index
        if self.ap.x[0] > self.ap.x[-1]:
            indx = len(self.ap.x) - indx
        
        
        if (indx >= len(self.ap.x)) or (indx == -1):
            #self.cx = None
            #self.cy = None
            self.ci = None
            return

        self.ci = indx
        #self.cx = self.x[indx]
        #self.cy = self.active_data[indx]
        return

    def calibrate(self,ap,display=True):
        if self.iref is None:
            print 'No reference aperture set'
            return None
        if ap is None:
            return
        shift = find_shift(self.aps[self.iref].active_data,ap.active_data)
        print 'Offset %i pixels from reference' % shift
        lines = ap.reidentify(self.aps[self.iref].lines,shift)

        if lines:
            print 'Located %i features from reference' % len(lines)
            fitted = ap.fit()
            if ap.fitted and display:
                self.display(ap.x,ap.active_data,reset=True)
        return
