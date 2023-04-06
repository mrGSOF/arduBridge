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

Class for interacting with a ArduShield.
The class has several methods for controlling the Dual H-Bridge circuit, SSR, current sensors,
temperature sensor, servo operation, and basic hardware test scripts.

The __init__ method initializes the object with a given ardu object and optional reference voltage
an_ref (defaults to 5.0). It also sets up a list of PWM channel pins and a list of servo channel pins,
which are both initialized to the same list of PWM pins.

By: Guy Soffer (gsoffer@yahoo.com)
Date: 19/Jun/2019
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = ["James Perry"]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time, math

class ArduBridge_Shield():
    def __init__(self, ardu, an_ref=5.0):
        print('GSOF_ArduBridge_HW v1.2')
        self.ardu = ardu
        self.an_ref = an_ref
        self.lsb = self.an_ref / 1024.0
        self.pwmCh = [3,5,6,9,10,11]    #< pwm-ch pin assignment
        self.servoCh = self.pwmCh       #< servo connectors on board are same as pwm connectors

    def getDmfChipCurrect(self, ch=3, units='b'):
        vBin = self.ardu.an.analogRead(ch)
        if units == 'b':
            return vBin
        elif units == 'A':
            Rsens = 10000 #< Ohm
            return vBin*self.lsb/Rsens
        else:
            print("Invalid units %s"%units)
            return -1.0

    def servoMode(self, ch, on):
        """Activate (1) or deactivate (0) servo mode on a given channel"""
        ofs = 0
        if not on:
            ofs += 100
        return self.ardu.gpio.pinMode( self.servoCh[ch] +ofs, 2)

    def servoSet(self, ch, val):
        """Set the servo angle"""
        return self.ardu.gpio.servoWrite( self.servoCh[ch], val)

    def servoScurve(self, ch, P0, P1, acc=200, DT=0.05):
        """Smooth transition from P0 to P1 at acceleration"""
        return self.ardu.gpio.servoScurve( self.servoCh[ch], P0, P1, acc)

    def pwmMode(self, ch, on):
        """ """
        if on:
            on = 0
        else:
            on = 1
        return self.ardu.gpio.pinMode( self.servoCh[ch], on)

    def pwmSet(self, ch, val):
        """Set the PWM output on the given channel (+/-255) """
        self.ardu.an.analogWrite(self.pwmCh[ch], val)

    def pwmA_init(self):
        """Initiat H-Bridge A """
        self.pwm_init(dirPin=2, pwmCh=0) #< pin2 and 3

    def pwmB_init(self):
        """Initiat H-Bridge B"""
        self.pwm_init(dirPin=4, pwmCh=1) #< pin4 and 5

    def pwm_init(self, dirPin, pwmCh):
        """Initiat the H-Bridge on the given channel"""
        self.ardu.gpio.pinMode(dirPin,0)                 #< Set dirPin as output
        self.ardu.gpio.digitalWrite(self.pwmCh[pwmCh],0) #< Set pwm to 0%

    def pwmA(self, p):
        """ Set the PWM value on H-BRIDGE A """
        self._pwm(p, dirPin=2, pwmCh=0)

    def pwmB(self, p):
        """ Set the PWM value on H-BRIDGE B """
        self._pwm(p,dirPin=4, pwmCh=1)

    def _pwm(self, p, dirPin, pwmCh):
        p = float(p)
        if p >= 0.0:
            di = 0
            if p > 100.0:
                p = 100.0
        else: #if p < 0.0:
            di = 1
            if p < -100.0:
                p = -100.0
            p = 100+p
            
        val = 255*p/100.0

        self.ardu.gpio.pinMode(dirPin, 0)
        self.ardu.gpio.digitalWrite(dirPin, di)
        self.ardu.an.analogWrite(self.pwmCh[pwmCh], val)

    def ssrA(self, v):
        """Set SSR-A on (1) or off (0)"""
        pin = 12
        if v < 0:
            v = 0
        elif v > 1:
            v = 1
        self.ardu.gpio.pinMode(pin,0)
        self.ardu.gpio.digitalWrite(pin,v)

    def ssrB(self, v):
        """Set SSR-B on (1) or off (0)"""
        pin = 13
        if v < 0:
            v = 0
        elif v > 1:
            v = 1
        self.ardu.gpio.pinMode(pin,0)
        self.ardu.gpio.digitalWrite(pin,v)

    def pwmA_cur(self):
        """Return the binary measured current on H-Bridge-A"""
        return self.ardu.an.analogRead(2)

    def pwmB_cur(self):
        """Return the binary measured current on H-Bridge-B"""
        return self.ardu.an.analogRead(3)

    def pwm_test(self, ch=range(0,6), val=[5,0], dly=0.2):
        """ """
        for pwm in ch:
            c = self.pwmCh[pwm]
            self.ardu.an.analogWrite(c, val[0])
            time.sleep(dly)
            self.ardu.an.analogWrite(c, val[1])

    def gpio_test(self, d=0.01):
        """ """
        pinList = range(2,14)
        for pin in pinList:
            self.ardu.gpio.pinMode(pin, 0)
            self.ardu.gpio.digitalWrite(pin, 1)
            if d > 0.0:
                time.sleep(d)
        pinList = range(13,1,-1)
        for pin in pinList:
            self.ardu.gpio.digitalWrite(pin, 0)
            if d > 0.0:
                time.sleep(d)
            #self.ardu.gpio.pinMode(pin, 1)

    def getTemp(self, ch=0):
        """Return the temperature from the embedded TC1047 sensor"""
        vBin = self.ardu.an.analogRead(ch)
        return self._TC1047(vBin)

    def _TC1047(self, bVal):
        """Return the temperature from the binary value"""
        volt = self.lsb*bVal
        C = (volt -0.5)/0.01
        return C

##    def setOsci(self, freq, dev=23):
##        freq = float(freq)
##        OCT = int(3.322*math.log10(freq/1039))
##        if (OCT >= 0) and (OCT <= 15):
##            DAC = int(2048.0 -(2078.0*(2.0**(10+OCT)))/freq)
##            if DAC < 0:
##                DAC = 0
##            val = (OCT<<12) +(DAC<<2)
##            print('DAC %d, OCT %d, VAL 0x%04x'%(DAC, OCT, val))
##            v = [0,0]
##            v[0] = (val>>8)&0xff
##            v[1] = val&0xff
##            self.ardu.i2c.writeRaw(dev, v)
##        else:
##            print('Frequency is out of range')
