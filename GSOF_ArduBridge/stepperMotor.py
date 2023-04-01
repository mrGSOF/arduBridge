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

Class to build an Stepper-Controller object.
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

class stepperMotor():
    def __init__(self, gpio=False, pinMap=[0,1,2,3], pos=0, maxV=10, acc=1, pwrPin=13):
        self.gpio = gpio
        self.pinMap = pinMap
        self.pwrPin = pwrPin
        self.maxV = 0.0
        self.acc = 0.0
        self.state=[[0,0,0,1],
                    [0,0,1,1],
                    [0,0,1,0],
                    [0,1,1,0],
                    [0,1,0,0],
                    [1,1,0,0],
                    [1,0,0,0],
                    [1,0,0,1]]
        self.steps = len(self.state)
        self.stepIdx = 0
        self.absolutePos = pos

    def config(self):
        self.gpio.pinMode(self.pwrPin, 0) #set all pins to outputs
        self.power(0)                     #power-off
       
        if self.gpio != False:
            for pin in self.pinMap:
                self.gpio.pinMode(pin, 0) #set all pins to outputs
                self.gpio.digitalWrite(pin, 0) #set all pins to outputs

    def power(self, val):
        if self.pwrPin != False:
            self.gpio.digitalWrite(self.pwrPin, val) #set all pins to outputs

    def moveTo(self, endPos, v=1, acc=1):
        endPos = int(endPos)
        self.power(1)                     #power-on
        direction = -1
        if  (endPos -self.absolutePos) > 0:
            direction = 1

        while(self.absolutePos != endPos):
            self.stepIdx += direction
            if self.stepIdx >= self.steps:
                self.stepIdx = 0
            elif self.stepIdx < 0:
                self.stepIdx = self.steps -1
                
            self.absolutePos += direction
            state = self.state[self.stepIdx]
            #print('Output %d, %s'%(self.stepIdx, str(state)))
            for coil, pinState in enumerate(state):
                pinNum = self.pinMap[coil]
                if self.gpio != False:
                    #print('coil# %d - %d'%(pinNum, pinState))
                    #time.sleep(0.1)
                    self.gpio.digitalWrite(pinNum, pinState)
        self.power(0)                     #power-off
        print('Position %d'%(self.absolutePos))

    def moveRel(self, dPos, v=1, acc=1):
        self.moveTo(self.absolutePos + dPos, v, acc)

###    def turn(self, speed=1, acceleration=1):
##
##    def sequencer(self, direction=1, speed=1, acceleration=1, cycles=100):
##        for nom in range(cycles):
##            print('Step: %d' %(step))
##            print('absolutePos: %d' %(absolutePos))
##            time.sleep(speed)
##            if direction == 1:
##                step += 1
##                absolutePos += 1
##            elif direction == 0:
##                step -= 1
##                absolutePos -= 1
##            if step == stepNum:
##                step = 0
##            if step < 0:
##                step = stepNum-1
    
        
        
    

