#!/usr/bin/env python

"""
    This file is part of GSOF_ArduBridge.

    GSOF_ArduBridge is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GSOF_ArduBridge is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GSOF_ArduBridge.  If not, see <https://www.gnu.org/licenses/>.

Class to build a simple periodic or single-shot thread.
When building the Class-Object you should supply a name (string) and a period time (float in Sec).
To start the thread use the objects mothod start() e.g: Obj.start()
To stop the thread use the objects mothod stop() e.g: Obj.stop()
To pause the thread use the objects mothod start() e.g: Obj.pause()
To continue the thread use the objects mothod cont() e.g: Obj.cont()
Your code should be located in the rocess method
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import threading, time

class BasicThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, nameID, Period, viewer={}):
        """T is the step period-time. If T == 0, The process will run only once"""
        #super(StoppableThread, self).__init__()
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.Period = Period
        self.T_Z = [0]*2
        self.name = nameID
        self.enable = True
        self.cycles = -1
        self.viewer = viewer
        self.lock = threading.Semaphore(True)
        if self.is_alive == None:
            self.is_alive = self.isAlive

        
    def addViewer(self, name, method):
        """Append the Viewer callback function to the Viewer list"""
        if method != False:
            if name not in self.viewer.keys():
                self.viewer[name] = method
            else:
                print('cannot over write the same viewer!')
    
    def remvoveViewer(self, name):
        """Remove the specified Viewer callback function"""
        if name in self.viewer.keys():
            self.viewer.pop([name])

    def teleUpdate(self, tele):
        """Call the all Viewer callback functions"""
        if len(self.viewer) > 0:
            for view in self.viewer:
                (self.viewer[view])(tele)
        else:
            print(str(tele))

    def stop(self):
        """Call this method to stop the thread"""
        #self.lock.acquire(True)
        self._stop_event.set()
        #self.enable = False
        #self.release()
        
    def start(self):#, phase=0.0):
        """Launch or resume the thread"""
        if self.is_alive():
            self.cont()
        else:
            self.T_Z[1] = time.time() -self.Period
            self.T_Z[0] = time.time()
            self.enable = True
            threading.Thread.start(self)

    def pause(self) -> bool:
        """Pause the thread (with the ability to resume)"""
        self.enable = False

    def cont(self) -> bool:
        """Resume the thread if paused"""
        self.enable = True
        
    def stopped(self):
        """Stop the thread (without the ability to resume or restart)"""
        return self._stop_event.is_set()

    def run(self):
        """The thread code that manage the periodic run, pause/cont and stop"""
        while ( not(self.stopped()) ):
            self.lock.acquire(True)
            if self.enable:
                ## \/ Code begins below \/
                self.process()
                ## /\  Code ends above  /\

            ## *** Calculating how much time to wait until the next execution ***
            if self.Period > 0:
                self.T_Z[1] = self.T_Z[0]
                self.T_Z[0] += self.Period
                sleepTime = self.T_Z[0] - time.time()
                if sleepTime < 0.05:
                    while sleepTime < 0.05:
                        self.T_Z[0] += self.Period
                        sleepTime += self.Period
                    s = '%s: Timing error - Skipping a cycle'%(self.name)
                    self.teleUpdate(s)
                    print(s)
                self.lock.release()
                time.sleep(sleepTime)
            else:
                self.stop()
        self.enable = False
        self.teleUpdate('%s: Terminated\n'%(self.name))

    def process(self):
        """The code that should be periodically executed is here"""
        ## \/ Code begins below \/
        self.teleUpdate('%s: called'%(self.name))
        ## /\  Code ends above  /\
