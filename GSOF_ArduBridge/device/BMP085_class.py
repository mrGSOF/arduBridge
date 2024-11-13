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
from GSOF_ArduBridge.device import BMP085_RM as RM

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

class BMP085():
    """Core functions to access the BMP085 device (Temperature & Pressure) via I2C-bus"""
    def __init__(self, i2c, dev=RM.I2C_AD):
        self.oss = 0 #0 to 3
        self._b5   = 4435
        self.id   = Reg( i2c, dev, RM.ID() )
        self.ver  = Reg( i2c, dev, RM.VER() )
        self.cmd  = Reg( i2c, dev, RM.CMD() )
        self.pres = Reg( i2c, dev, RM.ADC24() )
        self.temp = Reg( i2c, dev, RM.ADC16() )

        self._AC1 = {'val':0, 'reg':Reg( i2c, dev, RM.AC1() )}
        self._AC2 = {'val':0, 'reg':Reg( i2c, dev, RM.AC2() )}
        self._AC3 = {'val':0, 'reg':Reg( i2c, dev, RM.AC3() )}
        self._AC4 = {'val':0, 'reg':Reg( i2c, dev, RM.AC4() )}
        self._AC5 = {'val':0, 'reg':Reg( i2c, dev, RM.AC5() )}
        self._AC6 = {'val':0, 'reg':Reg( i2c, dev, RM.AC6() )}
        self._B1  = {'val':0, 'reg':Reg( i2c, dev, RM.B1() )}
        self._B2  = {'val':0, 'reg':Reg( i2c, dev, RM.B2() )}
        self._MB  = {'val':0, 'reg':Reg( i2c, dev, RM.MB() )}
        self._MC  = {'val':0, 'reg':Reg( i2c, dev, RM.MC() )}
        self._MD  = {'val':0, 'reg':Reg( i2c, dev, RM.MD() )}

    def getIdVer(self) -> list:
        """Read the device ID & version"""
        ID = self.id.read().get()
        VER= self.ver.read().get()
        return ID | VER

    def readEECalibrationValues(self) -> None:
        """Read all the internal calibration values of the device and store them in instance"""
        s = self
        for param in (s._AC1,s._AC2,s._AC3,s._AC4,s._AC4,s._AC5,s._AC6,s._B1,s._B2,s._MB,s._MC,s._MD):
            param["val"] = param["reg"].read().get()
            print( "EE:%s; Addr:0x%02x; Data:%d"%("", param["reg"]._reg.ad, param["val"]) )

    def startTempSample(self) -> None:
        """Command the device to start ADC of the temperature sensor"""
        self.cmd.write( smpT=True )

    def getTemperature_c(self) -> float:
        """Command sequence to sample & convert the pressure sensor"""
        """delay is the wait time until the ADC result can be read"""
        """Calibration values should be read prior to this command"""
        self.startTempSample()
        time.sleep(0.0045) #< 4.5 (ms) delay
        raw = self.temp.read().get()
        self.lastTemp, self._b5 = RM.calcTemperature_C(raw,
                                                      self._AC5['val'],
                                                      self._AC6['val'],
                                                      self._MC['val'],
                                                      self._MD['val'])
        return self.lastTemp

    def startPresSample(self, oss=-1) -> None:
        """Command the device to start ADC of the pressure sensor"""
        """oss is the converios mode (0 fastest ... 3 most accurate"""
        if (oss >= 0 ) and (oss <= 3):
            self.oss = oss
        self.cmd.write( smpP=True, oss=oss )

    def getPressure_pa(self, oss=0) -> float:
        """Command sequence to sample & convert the pressure sensor"""
        """delay is the time to wait until the ADC result can be read"""
        """oss is the converios mode (0 fastest ... 3 most accurate"""
        """Calibration values and temperature should be read prior to this command"""
        self.startPresSample(oss)
        time.sleep(0.0045*1.8**oss) #< ~4.5*1.8^oss (ms)
        raw = self.pres.read().get()
        pa = RM.calcPressure_Pa(raw,
                                self._AC1['val'],
                                self._AC2['val'],
                                self._AC3['val'],
                                self._AC4['val'],
                                self._B1['val'],
                                self._B2['val'],
                                oss=oss,
                                b5=self._b5)
        self.lastPres = pa
        return pa
