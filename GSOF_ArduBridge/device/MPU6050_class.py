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
from GSOF_ArduBridge.device import MPU6050_RM as RM
import time

class Reg():
    def __init__(self, i2c, dev, reg):
        self._i2c = i2c
        self._dev = dev
        self._reg = reg

    def read(self) -> None:
        vBytes = self._i2c.readRegister(self._dev, self._reg.ad, self._reg.size)
        if len(vBytes) == 1:
            vBytes = vBytes[0]
        return self._reg.fromBytes(vBytes)

    def write(self, **values) -> None:
        vByte = self._reg.toBytes(**values)
        self._i2c.writeRegister(self._dev, self._reg.ad, vByte)
        return self

    def readBurst(self, N) -> None:
        return self._i2c.readRegister(self._dev, self._reg.ad, N)

class MPU6050():
    """Class to access the MPU6050 device (3x gyro, 3x accelarometer, 1x temperature) via I2C-bus"""
   
    def __init__(self, i2c, dev=0x69, g=9.81):
        """ """
        self._g = g
        self._afs_sel = RM.AFS[0]
        self._gfs_sel = RM.GFS[0]
        self.selfTestX  = Reg( i2c, dev, RM.SelfTestX() )
        self.selfTestY  = Reg( i2c, dev, RM.SelfTestY() )
        self.selfTestZ  = Reg( i2c, dev, RM.SelfTestZ() )
        self.selfTestA  = Reg( i2c, dev, RM.SelfTestA() )
        self.smpRateDiv = Reg( i2c, dev, RM.SamplerRateDiv() )
        self.config     = Reg( i2c, dev, RM.Config() )
        self.gyroConfig = Reg( i2c, dev, RM.GyroConfig() )
        self.accConfig  = Reg( i2c, dev, RM.AccelConfig() )
        self.fifoEnable = Reg( i2c, dev, RM.FifoEn() )
        self.initPinCfg = Reg( i2c, dev, RM.InitPinCfg() )
        self.intEnable  = Reg( i2c, dev, RM.IntEnable() )
        self.intStatus  = Reg( i2c, dev, RM.IntStatus() )
        self.accX       = Reg( i2c, dev, RM.AccelXout() )
        self.accY       = Reg( i2c, dev, RM.AccelYout() )
        self.accZ       = Reg( i2c, dev, RM.AccelZout() )
        self.temp       = Reg( i2c, dev, RM.TempOut() )
        self.gyroX      = Reg( i2c, dev, RM.GyroXout() )
        self.gyroY      = Reg( i2c, dev, RM.GyroYout() )
        self.gyroZ      = Reg( i2c, dev, RM.GyroZout() )
        self.sigPathRst = Reg( i2c, dev, RM.SignalPathReset() )
        self.userCtrl   = Reg( i2c, dev, RM.UserCtrl() )
        self.pwrMgmt1   = Reg( i2c, dev, RM.PwrMgmt1() )
        self.pwrMgmt2   = Reg( i2c, dev, RM.PwrMgmt2() )
        self.fifoCount  = Reg( i2c, dev, RM.FifoCount() )
        self.fifoRw     = Reg( i2c, dev, RM.FifoRw() )
        self.whoAmI     = Reg( i2c, dev, RM.WhoAmI() )

    def resetSns(self, gyro=1, acc=1, temp=1):
        """Reset the selected sensors"""
        self.sigPathRst.write( gyro_rst=gyro, acc_rst=acc, temp_rst=temp )

    def resetDev(self, reset=1, sleep=1):
        """Reset the device"""
        self.pwrMgmt1.write( device_rst = int(bool(reset)),
                             sleep      = int(bool(sleep)),
                             cycle      = 0,
                             temp_dis   = 0,
                             clk        = RM.CLKSEL[0] )

    def setFifoEnable(self, enable=1 ,gyro=1, acc=1, temp=0):
        """Enable / disable the FIFO and rest it"""
        if enable:
            self.tempFifoEn.write(temp_fifo_en  = int(bool(temp)),
                                  accel_fifo_en = int(bool(acc)),
                                  xg_fifo_en    = int(bool(gyro)),
                                  yg_fifo_en    = int(bool(gyro)),
                                  zg_fifo_en    = int(bool(gyro)) )

        self.userCtrl.write(fifo_en=int(bool(enable)),
                            i2c_mst_en   = 0,
                            i2c_if_dis   = 0,
                            fifo_rst     = 1,
                            i2c_mst_rst  = 0,
                            sig_cond_rst = 0 )

    def reset(self):
        """Device reset sequence from RM-MPU-6000A-00 (v4.2) page 41"""
        self.resetDev(reset = 1)
        time.sleep(0.1)
        self.resetSns()

    def setConfig(self, ext_sync=RM.EXTSYNC[0], bw_hz=RM.DLPF[0], gfs_dps=RM.GFS[0], afs_g=RM.AFS[0], smpRate_hz=500):
        self.resetDev(reset = 0, sleep = 0)
        self.config.write(ext_sync=ext_sync, dlpf_hz=bw_hz)
        self.gyroConfig.write(fs_dps=gfs_dps)
        self._gfs_sel = RM.GFS.index(gfs_dps)
        self.accConfig.write(fs_g=afs_g)
        self._afs_sel = RM.AFS.index(afs_g)


        ### From RM-MPU-6000A-00 (v4.2) page 12
        gyroHz = 8000 #< hz
        if RM.DLPF.index(bw_hz) > 0:
            gyroHz = 1000 #< hz
        
        div = int((gyroHz/smpRate_hz)) -1 #< smpRateHz = gyroHz/(div +1)
        self.smpRateDiv.write(val=div)
        self.intEnable.write(fifo_overflow_en = 0,
                             i2c_mst_int_en   = 0,
                             data_rdy_en      = 0) #< No interrupts

    def setFifoEnable(self, fifoEnable=1,
                      accEn=1, tempEn=0, gyroEn=1,
                      slv2En=0, slv1En=0, slv0En=0):
        """Configure which sensors are pushed to the internal FIFO"""
        self.fifoEnable.write(accel_fifo_en=accEn, temp_fifo_en=tempEn,
                              xg_fifo_en=gyroEn, yg_fifo_en=gyroEn, zg_fifo_en=gyroEn,
                              slv2_fifo_en=slv2En, slv1_fifo_en=slv1En, slv0_fifo_en=slv0En )
        self.userCtrl.write( fifo_en=fifoEnable )
        return self

    def getFifoCnt(self):
        """Read how much bytes in the device FIFO"""
        dat = self.fifoCount.read().get()
        return dat["fifo_count"]
        
    def getFifo(self, tmplt, v=False):
        """
        Read the device FIFO (N is the number of bytes)
        Return a result vector [W0,W1,W2..WN] after converting each two bytes to WORD
        """
        smpSize  = 2*len(tmplt)
        maxReadSize = int(32/smpSize)*smpSize #< Maximum bytes to read without corrupting a sample and below 255 bytes

        ### Read all bytes from FIFO
        stream = []
        bytesInFifo = self.getFifoCnt()
        if v:
            T0 = time.time()
            print("FIFO has %d bytes"%bytesInFifo)

        while smpSize < bytesInFifo:
            if bytesInFifo >= maxReadSize:
                bytesToRead = maxReadSize
            else:
                bytesToRead = bytesInFifo
            stream += self.fifoRw.readBurst(bytesToRead)
            bytesInFifo -= bytesToRead
        if v:
            print("Reading FIFO took %1.4f seconds"%(time.time() -T0))

        ### Convert all samples to physical values
        i = 0
        samples = []
        bytesRead = len(stream)
        while i < bytesRead:
            j = i+smpSize
            if j < bytesRead:
                samples.append( self._convStream(stream[i:j], tmplt=tmplt) )
            i = j
        if v:
            print("With conversion took %1.4f seconds"%(time.time() -T0))

        return samples

    def getAll(self):
        """
        Read the output value of accl, temp, gyro.
        Return a result vector [AX,AY,AZ, T, GX, GY, GZ]
        """
        tmplt='aaatggg'
        stream = self.accX.readBurst( 2*len(tmplt) )
        return self._convStream(stream, tmplt=tmplt)

    def getAccels(self, N=3):
        """
        Read the output value of N accels sensors (X,Y,Z)
        Return a result vector [X,Y,Z]
        """
        tmplt = 'a'*N
        stream = self.accX.readBurst( N*2 )
        return self._convStream(stream, tmplt=tmplt)

##    def getAcc(self):
##        """Read all the accel sensors and convert them to phisical values"""
##        x = self.accX.read().get()["accel_xout"]
##        y = self.accY.read().get()["accel_yout"]
##        z = self.accZ.read().get()["accel_zout"]
##        return self._convAcc([x,y,z])

    def getGyros(self, N=3):
        """
        Read the output value of N gyros sensors (X,Y,Z)
        Return a result vector [X,Y,Z]
        """
        tmplt = 'g'*N
        stream = self.read_block( self.devID, self.REG.GXmsb, N*2 )
        return self._convStream(stream, tmplt=tmplt)

##    def getGyros(self):
##        """Read all the accel sensors and convert them to phisical values"""
##        x = self.gyroX.read().get()["gyro_xout"]
##        y = self.gyroY.read().get()["gyro_yout"]
##        z = self.gyroZ.read().get()["gyro_zout"]
##        return self._convGyro([x,y,z])

    def getTemp(self, units='c'):
        """Returns the temperature value to pysical or raw units"""
        raw = (self.temp.read().get())["temp_out"]
        return self._convTemp(raw, units)

    def _convStream(self, stream, tmplt='aaatggg'):
        N = len(tmplt)
        raw = [0]*N
        res = [0]*N
        i = 0
        while i < N:
            val = ( (stream[i*2]<<8) +stream[i*2 +1] )
            if val > 0x7FFF:
                val = -1*(((~val)+1)&0xffff)
            raw[i] = val
            i += 1
        for i, sns, in enumerate(tmplt):
            if sns == 'a':
                res[i] = self._convAcc(raw[i])
            elif sns == 'g':
                res[i] = self._convGyro(raw[i])
            elif sns == 't':
                res[i] = self._convTemp(raw[i])
        return res

    def wait(self, ms):
        T0 = time.time()
        T1 = T0 +ms/1000
        i = 0
        while time.time() < T1:
            i += 1
        return self

    def _convGyro(self, vGyro):
        """Convert accel raw reading to phisical values"""
        lsb = RM.gyroLsb(self._gfs_sel)
        if type(vGyro) != list:
            return lsb*vGyro
        else:
            for i,val in enumerate(vGyro):
                vGyro[i] = lsb*val
        return vGyro

    def _convAcc(self, vAcc):
        """Convert accel raw reading to phisical values"""
        lsb = RM.accLsb(self._afs_sel, self._g)
        if type(vAcc) != list:
            return lsb*vAcc
        else:
            for i,val in enumerate(vAcc):
                vAcc[i] = lsb*val
        return vAcc

    def _convTemp(self, raw, units='c'):
        """Returns the temperature value to pysical or raw units"""
        if units != 'r':
            raw = raw*RM.temp['a'] +RM.temp['b']   #< C
            if units == 'f':
                raw = raw*1.8 +32 #< F
        return raw
