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
"""

import time
from GSOF_ArduBridge.device import HMC5883_RM as RM

class Reg():
    def __init__(self, i2c, dev, reg):
        self._i2c = i2c
        self._dev = dev
        self._reg = reg

    def read(self):
        vBytes = self._i2c.readRegister(self._dev, self._reg.ad, self._reg.size)
        if len(vBytes) == 1:
            vBytes = vBytes[0]
        return self._reg.fromBytes(vBytes)

    def write(self, **values):
        vByte = self._reg.toBytes(**values)
        self._i2c.writeRegister(self._dev, self._reg.ad, vByte)
        return self

    def readBurst(self, N) -> list:
        return self._i2c.readRegister(self._dev, self._reg.ad, N)

class HMC5883():
    """Basic core function to access the HMC5338 device (3x axis magnetometer) via I2C-bus"""
    def __init__(self, i2c, dev=RM.I2C_AD):
        self.cfga   = Reg(i2c, dev, RM.CfgA() )
        self.cfgb   = Reg(i2c, dev, RM.CfgB() )
        self.mode   = Reg(i2c, dev, RM.Mode() )
        self.status = Reg(i2c, dev, RM.Status() )
        self.adcX   = Reg(i2c, dev, RM.AdcX() )
        self.adcZ   = Reg(i2c, dev, RM.AdcZ() )
        self.adcY   = Reg(i2c, dev, RM.AdcY() )
        self.id     = Reg(i2c, dev, RM.Id() )

        self.rawVals   = [0]*3
        self.gaussVals = [0.0]*3
        self.hardIronBias = [0]*3
        self.gn   = 0
        self.avgN = 1
        
    def _setCfgA(self, avgN=4, rate=7.5, meas=RM.MS[0]) -> None:
        """
        Configure the rate and build-in-test mode of the device
        avgN: {1,2,4,8}
        rate: {0.75, 1.5, 3, 7.5, 15, 30, 75, N.U.}
        meas: {Normal, positiveBias, negativeBias, N.U.}
        """
        self.avgN = avgN
        self.cfga.write( avgN=avgN, rate=rate, meas=meas )
    
    def _setCfgB(self, maxGauss=1.3) -> None:
        """
        Configure the gain of the device
        maxGauss: {0.88, 1.3, 1.9, 2.5, 4.0, 4.7, 5.6, 8.1}
        """
        self.gn = RM.GNrange.index(maxGauss)
        self.cfgb.write( gn=self.gn )
 
    def _setMode(self, hs=0, mode=RM.MD[1]) -> None:
        """
        Configure the sampling mode of the device
        mode: {Continuous, Single, Idle, Sleep}
        """
        self.mode.write( hs=hs, mode=mode )

    def setCfg(self, avgN=4, rate=7.5, meas=RM.MS[0], maxGauss=4.0, mode=RM.MD[1]):
        """
        avgN: {1,2,*4,8}
        rate: {0.75, 1.5, 3, *7.5, 15, 30, 75, -1}
        meas: {*Normal, positiveBias, negativeBias, N.U.}
        maxGauss: {0.88, 1.3, *1.9, 2.5, 4.0, 4.7, 5.6, 8.1}
        mode: {Continuous, *Single, Idle, Sleep}
        """
        self._setCfgA(avgN=avgN, rate=rate, meas=meas)
        self._setCfgB(maxGauss)
        self._setMode(hs=0, mode=mode)
        return self

    def startHardIronClibration(self, N=16):
        self._setCfgA(avgN=4, rate=7.5, meas='positiveBias')
        posBias = [0]*3
        for i in range(N):
            time.sleep(0.1)
            sample = self.getSingleGauss()
            for i,val in enumerate(sample):
                posBias[i] += val/N
        print("With positive bias: ", posBias)

        self._setCfgA(avgN=4, rate=7.5, meas='negativeBias')
        negBias = [0]*3
        for i in range(N):
            time.sleep(0.1)
            sample = self.getSingleGauss()
            for i,val in enumerate(sample):
                negBias[i] += val/N
        print("With negative bias: ", negBias)
        
        self._setCfgA(avgN=4, rate=7.5, meas='normal')
        self.hardIronBias[0] = (posBias[0] +negBias[0])/2
        self.hardIronBias[1] = (posBias[1] +negBias[1])/2
        self.hardIronBias[2] = (posBias[2] +negBias[2])/2
        print("Average bias: ", self.hardIronBias)
        
        
    def getCfg(self):
        """Reaturns the entire device configuration"""
        val  = self.cfga.read().get()
        val |= self.cfgb.read().get()
        val |= self.mode.read().get()
        return val

    def getID(self) -> str:
        """Read the device ID 'H43'"""
        return self.id.read().get()

    def getMode(self):
        """Returns the device mode register"""
        return self.mode.read().get()

    def getStatus(self):
        """Returns the device status register"""
        return self.status.read().get()

    def startSample(self, mode=RM.MD[1]):
        """Command the device to start sampling all 3x channels"""
        """mode: {continuous, *single, idle, sleep}"""
        self._setMode( mode=mode )
            
    def getConversion(self, N=3):
        """Read the output value of the device ADC (N is the number of words)"""
        """Return the corrected order result vector [X,Y,Z]"""
        dat = self.adcX.readBurst( N*2 )
        raw = [0]*N
        gauss = [0]*N
        i = 0
        while i < N:
            val = ( (dat[i*2]<<8) +dat[i*2+1] )
            if val > 0x7FFF:
                val = -1*(((~val)+1)&0xffff)
            raw[i] = val
            gauss[i] = RM.calcGauss(val, self.gn)
            i += 1

        if N == 3:
            self.rawValues   = [raw[0], raw[2], raw[1]]
            self.gaussValues = [gauss[0] -self.hardIronBias[0],
                                gauss[2] -self.hardIronBias[1],
                                gauss[1] -self.hardIronBias[2]]
        else:
            self.rawValues   = raw
            self.gaussValues = gauss
        return self.gaussValues

    def getSingleGauss(self, N=3, delay=0.01):
        """
        Command sequence to sample & convert all the magnetometer sensors
        delay is the time to wait until the ADC result can be read
        Calibration values should be set prior to this command
        """
        self.startSample(mode='single')   #< Start a single acquisition
        time.sleep(delay)
        return self.getConversion(N)  #< Read all sensors results

"""
Below is an example of a temperature compensation process using positive self test method:
1. If self test measurement at a temperature 'when the last magnetic calibration was done':
    X_STP = 400
    Y_STP = 410
    Z_STP = 420
2. If self test measurement at a different tmperature:
    X_STP = 300 (Lower than before)
    Y_STP = 310 (Lower than before)
    Z_STP = 320 (Lower than before)
    Then
    X_TempComp = 400/300
    Y_TempComp = 410/310
    Z_TempComp = 420/320
3. Applying to all new measurements:
    X = X * X_TempComp
    Y = Y * Y_TempComp
    Z = Z * Z_TempComp
    Now all 3 axes are temperature compensated, i.e. sensitivity is same as 'when the last magnetic calibration was
    done'; therefore, the calibration coefficients can be applied without modification.
4. Repeat this process periodically or, for every DT degrees of temperature change measured, if available.
"""
