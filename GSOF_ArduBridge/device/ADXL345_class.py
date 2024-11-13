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

from GSOF_ArduBridge.device import ADXL345_RM as RM

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

class ADXL345():
    """Function to access the ADXL345 device (3x axis accelarometer) via I2C-bus"""
    def __init__(self, i2c, dev=0x69):
        self.id = Reg( i2c, dev, RM.Id() )
        self.ThrsTap = Reg( i2c, dev, RM.ThrsTap() )
        self.ofsx    = Reg( i2c, dev, RM.OfsX() )
        self.ofsy    = Reg( i2c, dev, RM.OfsY() )
        self.ofsz    = Reg( i2c, dev, RM.OfsZ() )
        self.dur     = Reg( i2c, dev, RM.Dur() )
        self.latent  = Reg( i2c, dev, RM.Latent() )
        self.window  = Reg( i2c, dev, RM.Window() )
        self.actinactctrl = Reg( i2c, dev, RM.ActInactCtrl() )
        self.acttapstatus = Reg( i2c, dev, RM.ActTapStatus() )
        self.bwrate  = Reg( i2c, dev, RM.BwRate() )
        self.pwrctrl = Reg( i2c, dev, RM.PowerCtrl() )
        self.intenable = Reg( i2c, dev, RM.IntEnable() )
        self.intmap  = Reg( i2c, dev, RM.IntMap() )
        self.intsource  = Reg( i2c, dev, RM.IntSource() )
        self.dataformat = Reg( i2c, dev, RM.DataFormat() )
        self.window  = Reg( i2c, dev, RM.Window() )
        self.datax  = Reg( i2c, dev, RM.DataX() )
        self.datay  = Reg( i2c, dev, RM.DataY() )
        self.dataz  = Reg( i2c, dev, RM.DataZ() )
        self.fifostatus = Reg( i2c, dev, RM.FifoStatus() )

        self.rawAdcValues = [0]*3
        self.acclValues = [0.0]*3
    
    def getAcc(self, N=3):
        """Read the output value of the device ADC (N is the number of words)"""
        """Return a result vector [X,Y,Z]"""
        dat = self.read_block( self.devID, self.REG.Xlsb, N*2 )
        res = [0]*N
        i = 0
        while i<N:
            val = ( (dat[i*2 +1]<<8) +dat[i*2] )
            if val > 0x7FFF:
                val = -1*(((~val)+1)&0xffff)
            res[i] = val
            i += 1
        self.RawAdcValues = res
        return res

    def getOfs(self, N=3):
        """Read the ofset values of the device (N is the number of values)"""
        """Return a result vector [X,Y,Z]"""
        dat = self.read_block( self.devID, self.REG.OfsX, N )
        res = [0]*N
        i = 0
        while i<N:
            val = ( dat[i] )
            if val > 0x7F:
                val = -1*(((~val)+1)&0xff)
            res[i] = val*4
            i += 1
        return res

    def setOfs(self, x=None, y=None, z=None):
        """Write the ofset values to the device 15.6*9.81 m/s^2/lsb"""
        if x != None:
            self.ofsx.write( x/1000 )
        if y != None:
            self.ofsy.write( y/1000 )
        if z != None:
            self.ofsz.write( z/1000 )
        return self

    def startCap(self, mode=1):
        """Command the device to start/stop sampling all 3x channels"""
        if mode == 0:
            self.WritePwr( meas=0, sleep=1 ) #Stop
        else:
            self.WritePwr( meas=1, sleep=0 ) #Start

    def startConv(self):
        """Read all the accelarometers sensors and convert them to phisical values"""
        """Calibration values should be set prior to this command"""
        self.GetADC(3)          #read all sensors results
        self.AcclValues = self.Calc(ch=-1, Mbin=[])  #convert the results
        return self.AcclValues
