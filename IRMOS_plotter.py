#! /usr/bin/env python
import argparse
import matplotlib.pyplot as plt
import matplotlib.patheffects as PE
import numpy as np
import pyfits
from peakdetect import peakdetect
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


class Plotter(object):
    def __init__(self, filename, aperture, linelist=None,load=False):

        self.filename = filename
        self.linelist = linelist
        self.aperture = aperture
        
        # get database information
        self.databasedir = os.path.join(os.path.dirname(filename),'database')
        self.database = os.path.join(self.databasedir,os.path.splitext(os.path.basename(filename))[0]+'.cal')
        self.section = os.path.basename(self.filename)
        self.section = '%s_%i' % (os.path.splitext(self.section)[0],self.aperture)
        self.orig = pyfits.getdata(filename)[aperture]
        self.active_data = self.orig
        self.x = range(0,len(self.active_data))
        self.ix = range(0,len(self.active_data))

        # search radius for max pix on each line
        self.search = 10
        self.load = load
        self.lines = []
        
        if load:
            #load from database
            self._load_lines()
            self.fit()
            

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
        self.subparser.add_argument('--s',action='store_true',help='Save to database')
        self.subparser.add_argument('--l',action='store_true',help='Load from database')
        return

    def _initialize_figure(self):
        # initialize figure
        self.fig = plt.figure()
        self.fig.canvas.mpl_disconnect(self.fig.canvas.manager.key_press_handler_id)
        self.keycid = self.fig.canvas.mpl_connect('key_press_event',self.onkey)
        self.motioncid = self.fig.canvas.mpl_connect('motion_notify_event',self.mouse_move)
        self.pid = None

        # Plot initial data
        self.display(self.x,self.active_data,lines=self.lines,reset=True)

        plt.show()
        return self.fig

    def _load_lines(self):
        #read lines from database
        if not os.path.exists(self.database):
            print 'No database file found for %s' % self.filename
            return

        config = ConfigParser.SafeConfigParser()
        print 'Loading calibration from %s' % self.database
        config.read(self.database)
        if not config.has_section(self.section):
            print 'Aperture %i not found in %s' % self.database
            return

        if not config.has_option(self.section,'lines'):
            print 'Aperture %i calibration not found in %s' % self.database
            return

        featurelist = get_featurelist(config.get(self.section,'lines'))
        print 'Loaded %i features' % len(featurelist)
        ys = [self.find_peak(x[0])[1] for x in featurelist]
        self.lines = [[x[0],y,x[1],None] for x,y in zip(featurelist,ys)]
        return self.lines



    def displaylines(self,lines=None,color='r'):
        arrh = plt.gca().get_ylim()[1]*0.05
        texth = arrh*2
        #print self.lines
        if not lines:
            lines = self.lines

        pids = []
        for line in lines:
            ix,y,s,pid = line  #index of x, y data, string, pid
            line[3] = plt.annotate(s,
                                   xytext=(self.x[ix],y+texth),
                                   xy=(self.x[ix],y+arrh),
                                   rotation=90,va='bottom',ha='center',
                                   arrowprops=dict(arrowstyle="-",color=color),
                                   fontsize=10)
            pids.append(line[3])
        return pids

    def display(self,x, data,lines=None,flip=False,reset=False):
        if plt.gca():
            xlim = plt.gca().get_xlim()
            ylim = plt.gca().get_ylim()

        self.fig.clf()
        
        if isinstance(data,str):
            data = pyfits.getdata(data)

        plt.plot(x,data,lw=1.5,color='k')

        if not reset:
            plt.xlim(xlim)
            plt.ylim(ylim)

        if flip:
            plt.xlim(plt.gca().get_xlim()[::-1])

        self.displaylines(lines)
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

        if args.s:
            fitted = self.fit()
            if fitted:
                m,b,rms = fitted
                self.display(self.x,self.active_data,reset=True)
            else:
                print 'No fit.'
                return
            
            #mkdir
            try:
                os.mkdir(self.databasedir)
            except OSError:
                print 'Directory %s exists.' % self.databasedir

            section = self.section

            config = ConfigParser.SafeConfigParser()
            if os.path.exists(self.database):
                config.read(self.database)
                           
            try:
                config.add_section(section)
            except ConfigParser.DuplicateSectionError:
                print 'Overwriting previous calibration'
                
            featurelist = set_featurelist(self.lines)
            config.set(section,'CRDELT1','%.3f'%np.abs(m))
            config.set(section,'CRPIX1','1')
            config.set(section,'CRVAL1','%.3f'%b)
            config.set(section,'RMS','%.3f'%rms)
            config.set(section,'lines',featurelist)

            with open(self.database,'w') as configfile:
                print 'Writing aperture %i to %s' % (self.aperture, self.database)
                config.write(configfile)
            
            if args.q:
                plt.close()
                return 'Q'
            else:
                return

        if args.l:
            self._load_lines()
            self.fit()
            self.display(self.x,self.active_data,reset=True)
            return

        if args.w == 'f':
            self.display(self.x,self.active_data,flip=True)

        elif args.w == 'a':
            self.display(self.x,self.active_data,reset=True)

        if args.r:
            self.active_data = self.orig
            self.x = range(0,len(self.active_data))
            self.ix = range(0,len(self.active_data))
            self.display(self.x,self.active_data,reset=True)

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
                    self.display(self.x,self.active_data)
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
                        y = self.active_data[ix]
                        self.lines.append([ix,y,s,None])

                    self.pausetext = '-'
                    self.display(self.x,self.active_data)
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

            localmax = self.find_peak(cm)

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
            if not self.lines:
                return
            
            # grab mouse position
            cm = self.ci
            if cm is None:
                return

            #find closest line
            #print self.lines
            #print cm

            linexs = np.array([line[0] for line in self.lines])
            #print linexs,cm
            cidx = np.argmin(np.abs(linexs - cm))
            #idx = np.searchsorted(linexs,cm)
            #print idx
            self.lines[cidx][3].remove()
            del self.lines[cidx]
            self.fig.canvas.draw()
            return

        if event.key == 'f':
            self.fit()
            self.display(self.x,self.active_data,reset=True)
            
            return
            

    def mouse_move(self, event):
        if not event.inaxes:
            self.ci = None
            #self.cx = None
            #self.cy = None
            return

        x, y = event.xdata, event.ydata
        sortx = np.sort(self.x)
        indx = np.searchsorted(sortx, [x])[0]

        # if self.x was reversed, switch index
        if self.x[0] > self.x[-1]:
            indx = len(self.x) - indx
        
        
        if (indx >= len(self.x)) or (indx == -1):
            #self.cx = None
            #self.cy = None
            self.ci = None
            return

        self.ci = indx
        #self.cx = self.x[indx]
        #self.cy = self.active_data[indx]
        return


    def find_peak(self,cm):
        localmax,localmin = peakdetect(self.active_data[cm-self.search:cm+self.search],x_axis=range(0,len(self.x))[cm-self.search:cm+self.search],lookahead=self.search/4)
        localmax = sorted(localmax,key=lambda x:x[1])[-1]

        return localmax

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
        return (m,b,rms)

        #plt.figure()
        #plt.plot(pix,waves,'ro')
        #plt.plot(pix,np.poly1d(p[0])(pix),'b-')
        #plt.show()

        
