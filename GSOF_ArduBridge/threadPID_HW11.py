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
- Designed to work with the GSOF-ArduShield board.
- Exponential pulse-shaping filter on the control signal.
- Moving average filter on the feedback.
- Support for real-Time change of moving average filter lenght.
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
    def __init__(self, bridge, nameID, Period, fbPin, outFunc, viewer={}):
        """T is the step period-time. If T == 0, The process will run only once"""
        #super(StoppableThread, self).__init__()
        BT.BasicThread.__init__(self, nameID=nameID, Period=Period, viewer=viewer)
        self.ardu = bridge      #The Arduino-Bridge object
        self.outFunc = outFunc  #The function to control the output signals to the electronics
        self.fbPin = fbPin      #Pin# that should be read as the feedback
        self.ct = 25.0          #Init value of target value
        self.ct_now = self.ct
        self.RC_div_DT = 22.0   #Period #Exponential pulse-shaping coef'
        self.PID = PidAlgorithm.PidAlgorithm( P=1, I=0, D=0)
        self.PID.outMax = 100   #Maximum output value
        self.PID.outMin = -100  #Minimum output value
        
        self.enOut = False
        self.enInput = True

        #Coefficients for linear approximation temperature calculation
        self.a = -0.7
        self.b = -1010.0
        
        #Coefficients for Steinhart temperature calculation
        self.RTDstd = 100000
        self.Tstd = 25.0
        self.Kbeta = 4250 #4040
        self.Rser = 4700  #100000

        self.T0 = time.time()
        self.ctrl_Z0 = time.time()
        self.ctrl_Rise = -1
        self.ctrl_Settle = -1

        self.Rise_tolerance = 2
        self.Settle_tolerance = 1

        self.filterN = 1
        self._filterN = 0
        
    def enIO(self, val=True) -> None:
        self.enOut = val
        self.enInput = val

    def start(self) -> None:
        """Start the controller"""
        self.T0 = time.time()
        BT.BasicThread.start(self)
        if self.enOut:
            print('%s: Started ON line'%(self.name))
        else:
            print('%s: Started OFF line'%(self.name))

    def process(self) -> None:
        """The controllers"""
        #Get the feedback
        feedback = 25.0
        if self.enInput:
            feedback = self.getFeedback()

        #If the moving average filter lenght was change during run time
        if self._filterN != self.filterN:
            self._filterN = self.filterN
            if self._filterN > 1:
                print('New filter. N=%d'%(self._filterN))
                self.fbFilter = movAvg.Stat_Recursive_X_Array( X=[feedback]*self._filterN )
        
        #Moving avarage for the feedback signal
        if self._filterN > 1:
            self.fbFilter.step(feedback)
            feedback = self.fbFilter.Ex()
        
        #Calculate the control-loop
        dt = time.time() -self.T_Z[1] #DT
        self.ct_now += dt*(self.ct -self.ct_now)/self.RC_div_DT #Exponential transition curve
        out = self.PID.NextStep(ctrl=self.ct_now, feedback=feedback, dt=dt)
           
##        #Filtering the feedback signal only for the telemetry
##        if self._filterN > 1:
##            self.fbFilter.step(feedback)
##            feedback = self.fbFilter.Ex()
##            self.PID.feedback[0] = feedback

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

    def stop(self) -> None:
        """Terminate the controller (thread)"""
        self.setOutput(0)
        BT.BasicThread.stop(self)

    def pause(self) ->None:
        """Pause the controller"""
        self.setOutput(0)
        BT.BasicThread.pause(self)

    def ctrl(self, target) -> None:
        """Set the target set-point (temperature)"""
        self.ct = target
        self.ctrl_Rise = -1
        self.ctrl_Settle = -1
        self.ctrl_Z0 = time.time()

    def setOutput(self, val) -> None:
        """Set the controllers output (H-Bridge)"""
        self.outFunc(val)

    def getFeedback(self) -> float:
        """Read the feedback (temperature sensor)"""
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

