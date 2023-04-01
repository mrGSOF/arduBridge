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

Class to build a simple real-time PID control-loop as a thread.
Features:
- Exponential pulse-shaping filter on the control signal.
- Moving average filter on the feedback.
= Works with the old H-bridge setup.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import math, time
from GSOF_ArduBridge import threadBasic as BT
from GSOF_ArduBridge import PidAlgorithm
from GSOF_ArduBridge import movAvg

class ArduPidThread(BT.BasicThread):
    """
    """
    def __init__(self, bridge, nameID, Period, fbPin, outPin, dirPin, viewer={}):
        """
        T is the step period-time. If T == 0, The process will run only once.
        """
        #super(StoppableThread, self).__init__()
        BT.BasicThread.__init__(self, nameID=nameID, Period=Period, viewer=viewer)
        self.ardu = bridge   #The Arduino-Bridge object
        self.fbPin = fbPin   #save the pin# that should be used
        self.outPin = outPin #save the pin# that should be used
        self.dirPin = dirPin #save the pin# that should be used
        self.ct = 25.0       #Init value of target value
        self.ct_now = self.ct
        self.RC_div_DT = 100.0 #Period #Exponential pulse-shaping coef'
        self.PID = PidAlgorithm.PidAlgorithm( P=1, I=0, D=0)
        self.PID.outMax = 100   #Maximum output value
        self.PID.outMin = -100  #Minimum output value

        if self.ardu:
            self.ardu.gpio.pinMode(self.dirPin, 0) #Set the pins direction to output
        self.enOut = False
        self.enInput = True

        #Coefficients for linear approximation temperature calculation
        self.a = -0.7
        self.b = -1010.0
        
        #Coefficients for Steinhart temperature calculation
        self.RTDstd = 100000
        self.Tstd = 25.0
        self.Kbeta = 4040  #4250
        self.Rser = 98400  #4700

        self.T0 = time.time()
        self.ctrl_Z0 = time.time()
        self.ctrl_Rise = -1
        self.ctrl_Settle = -1

        self.Rise_tolerance = 2
        self.Settle_tolerance = 1

        #Moving avarage for the feedback signal
        self.fbFilter = movAvg.Stat_Recursive_X_Array( X=[25]*4 )
        
    def enIO(self, val=True):
        self.enOut = val
        self.enInput = val

    def start(self):
        self.T0 = time.time()
        BT.BasicThread.start(self)
        if self.enOut:
            print('%s: Started ON line'%(self.name))
        else:
            print('%s: Started OFF line'%(self.name))

    def process(self):
        """
        Your PID code should go here.
        """
        ## \/ Code begins below \/
        #Get the feedback
        feedback = 25.0
        if self.enInput:
            feedback = self.getFeedback()
        self.fbFilter.step(feedback)
        feedback = fbFilter.Ex()
        
        #Calculate the control-loop
        dt = time.time() -self.T_Z[1] #Calculate the DT value
        self.ct_now += dt*(self.ct -self.ct_now)/self.RC_div_DT #Exponential transition curve
        out = self.PID.NextStep(ctrl=self.ct_now, feedback=feedback, dt=dt)
           
        #Set the output
        if self.enOut:
            self.setOutput(val=out)

        #Send telemetry
        self.teleUpdate( 'T: %6.2f, %s'%( time.time() -self.T0, self.PID.getStatus()))

        #Measure rise-time
        if self.ctrl_Rise == -1:
            if abs(feedback-self.ct) < self.Rise_tolerance:
                self.ctrl_Rise = time.time() -self.ctrl_Z0
                print('Rise-Time: %6.2f'%(self.ctrl_Rise))
                
        #Measure settle-time
        elif self.ctrl_Settle == -1:
            if abs(feedback-self.ct) < self.Rise_tolerance:
                self.ctrl_Settle = time.time() -self.ctrl_Z0
                print('Settle-Time: %6.2f'%(self.ctrl_Settle))
        ## /\  Code ends above  /\

    def stop(self):
        self.setOutput(0)
        BT.BasicThread.stop(self)

    def pause(self):
        self.setOutput(0)
        BT.BasicThread.pause(self)

    def ctrl(self, target):
        self.ct = target
        self.ctrl_Rise = -1
        self.ctrl_Settle = -1
        self.ctrl_Z0 = time.time()

    def setOutput(self, val):
        #set H-bridge direction
        h = 0 #Heating up
        if val < 0:
            h = 1 #Cooling down
            val = -val
        if self.ardu:
            self.ardu.gpio.digitalWrite(self.dirPin, h)

        #set output value
        if self.ardu:
            self.ardu.an.analogWrite(self.outPin, val)

    def getFeedback(self):
        #Steinhart formula
        Tbin = self.ardu.an.analogRead(self.fbPin)
        if (Tbin <= 0) or (Tbin >= 1023):
            print('TempSensor out of range! Tbin == %d'%(Tbin))
            Tbin = 950
            return self.ct
        
        Tbin = (1023.0 / Tbin) -1
        Tbin = self.Rser / Tbin
        Cdeg = Tbin / self.RTDstd
        if Cdeg <= 0:
            print('Temp calculation error!')
            return 25
        
        Cdeg = math.log(Cdeg)
        Cdeg /= self.Kbeta
        Cdeg += 1.0/(self.Tstd +273.15)
        Cdeg = 1.0/Cdeg
        Cdeg -= 273.15
        return Cdeg
        #return self.a*(self.ardu.an.analogRead(self.fbPin) +self.b)

