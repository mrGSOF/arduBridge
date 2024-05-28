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

Class to build a simple electrode sequencer thread.
When building the Class-Object you should supply a gpioObject, name (string), period time,
On time and sequense list.
Your code should be located in the process method
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = ["James Perry"]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time
from GSOF_ArduBridge import threadBasic as bt

class ArduElecSeqThread(bt.BasicThread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """
    def __init__(self, gpio, nameID, Period, onTime, elecList, nameToPin=False, viewer={}):
        """
        Period is the step period-time. If T == 0, The process will run only once.
        """
        #super(StoppableThread, self).__init__()
        bt.BasicThread.__init__(self, nameID=nameID, Period=Period, viewer=viewer)
        self.gpio = gpio #The Arduino-Bridge object
        self.onTime = onTime #Save the pin# that should be used
        self.elecList = elecList #Save the pin# that should be used
        self.nameToPin = nameToPin
        self.reset()
        self.enOut = False

    def cont(self, cyc=False):
        if cyc != False:
            self.cycles = cyc
        self.enable = True

    def start(self, cyc=False):
        self.cont(cyc)
        bt.BasicThread.start(self)
        if self.enOut:
            print('%s: Started ON line'%(self.name))
        else:
            print('%s: Started OFF line'%(self.name))

    def reset(self):
        self.cycles = -1
        self.enable = False
        self.idx = 0
    
    def process(self):
        ## \/ Code begins below \/
        if self.cycles != 0:
            electrodes = self.elecList[self.idx]
            if type(electrodes) == int:
                electrodes = [electrodes]

            for elec in electrodes:
                if self.nameToPin != False:
                    elec = self.nameToPin(elec)
                if self.enOut:
                    self.gpio.pinWrite(elec, 1)
                self.teleUpdate('%s, E%d: 1'%(self.name, elec))

            if self.onTime < self.Period*0.9:
                time.sleep(self.onTime)
            else:
                self.teleUpdate('%s, Error - onTime too long %6.3f[sec]'%(self.name, self.onTime))

            for elec in electrodes:
                if self.nameToPin != False:
                    elec = self.nameToPin(elec)
                if self.enOut:
                    self.gpio.pinWrite(elec, 0)
                self.teleUpdate('%s, E%d: 0'%(self.name, elec))

            self.idx += 1
            if self.idx >= len(self.elecList):
                self.idx = 0
                if self.cycles > 0:
                    self.cycles -= 1
                    if self.cycles == 0:
                        self.pause()
        ## /\  Code ends above  /\
    
class MoveElecSeqThread(ArduElecSeqThread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """
    def __init__(self, gpio, nameID, Period, onTime=-1, elecList=[], nameToPin=False):
        """
        Period is the step period-time. If T == 0, The process will run only once.
        """
        #super(StoppableThread, self).__init__()
        bt.BasicThread.__init__(self, Period=Period, nameID=nameID)
        self.gpio = gpio #The Arduino-Bridge object
        self.elecList = elecList #Save the pin# that should be used
        self.nameToPin = nameToPin
        self.reset()
        self.enOut = False

    def reset(self):
        self.cycles = -1
        self.enable = False
        self.idx_Z0 = 0
        self.idx_Z2 = -2
#        for elec in self.elecList:
#            self.gpio.pinWrite(elec, 0)

    def process(self):
        ## \/ Code begins below \/
        if self.cycles != 0:
            self.queue = 1
            elecON = self.elecList[self.idx_Z0]
            if type(elecON) == int:
                elecON = [elecON]

            elecOFF = []
            if self.idx_Z2 >= 0:
                elecOFF = self.elecList[self.idx_Z2]

            if type(elecOFF) == int:
                elecOFF = [elecOFF]

            for elec in elecON:
                if self.nameToPin != False:
                    elec = self.nameToPin(elec)
                if self.enOut:
                    self.gpio.pinWrite(elec, 1)
                self.teleUpdate('%s, E%d: 1'%(self.name, elec))

            for elec in elecOFF:
                if self.nameToPin != False:
                    elec = self.nameToPin(elec)
                if self.enOut:
                    self.gpio.pinWrite(elec, 0)
                self.teleUpdate('%s, E%d: 0'%(self.name, elec))

            self.idx_Z2 += 1
            if self.idx_Z2 >= len(self.elecList):
                self.idx_Z2 = 0

            self.idx_Z0 += 1
            if self.idx_Z0 >= len(self.elecList):
                self.idx_Z0 = 0
                if self.cycles > 0:
                    self.cycles -= 1
                    if self.cycles == 0:
                        lastElec = range(0,(len(self.elecList) -self.idx_Z2))
                        for i in lastElec:
                            elec = self.elecList[self.idx_Z2+i]
                            if self.enOut:
                                self.gpio.pinWrite(elec, 0)
                            self.teleUpdate('%s, E%d: 0'%(self.name, elec))
                        self.reset()
                        self.queue = 0
        ## /\  Code ends above  /\
