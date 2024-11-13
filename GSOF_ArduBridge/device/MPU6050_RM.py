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
I2C_AD = 0x69

AUX_VDDIO      = 0x01
SELF_TEST_X    = 0x0D
SELF_TEST_Y    = 0x0E
SELF_TEST_Z    = 0x0F
SELF_TEST_A    = 0x10
SMPRT_DIV      = 0x19
CONFIG         = 0x1A
GYRO_CONFIG    = 0x1B
ACCEL_CONFIG   = 0x1C
FF_THR         = 0x1D
FF_DUR         = 0x1E
MOT_THR        = 0x1F
MOT_DUR        = 0x20
ZRMOT_THR      = 0x21
ZRMOT_DUR      = 0x22
FIFO_EN        = 0x23
I2C_MST_CTRL   = 0x24
I2C_SLV0_ADDR  = 0x25
I2C_SLV0_REG   = 0x26
I2C_SLV0_CTRL  = 0x27
I2C_SLV1_ADDR  = 0x28
I2C_SLV1_REG   = 0x29
I2C_SLV1_CTRL  = 0x2A
I2C_SLV2_ADDR  = 0x2B
I2C_SLV2_REG   = 0x2C
I2C_SLV2_CTRL  = 0x2D
I2C_SLV3_ADDR  = 0x2E
I2C_SLV3_REG   = 0x2F
I2C_SLV3_CTRL  = 0x30
I2C_SLV4_ADDR  = 0x31
I2C_SLV4_REG   = 0x32
I2C_SLV4_DO    = 0x33
I2C_SLV4_CTRL  = 0x34
I2C_SLV4_DI    = 0x35
I2C_MST_STATUS = 0x36
INT_PIN_CFG    = 0x37
INT_ENABLE     = 0x38
INT_STATUS     = 0x3A
ACCEL_XOUT_H   = 0x3B
ACCEL_XOUT_L   = 0x3C
ACCEL_YOUT_H   = 0x3D
ACCEL_YOUT_L   = 0x3E
ACCEL_ZOUT_H   = 0x3F
ACCEL_ZOUT_L   = 0x40
TEMP_OUT_H     = 0x41
TEMP_OUT_L     = 0x42
GYRO_XOUT_H    = 0x43
GYRO_XOUT_L    = 0x44
GYRO_YOUT_H    = 0x45
GYRO_YOUT_L    = 0x46
GYRO_ZOUT_H    = 0x47
GYRO_ZOUT_L    = 0x48
EXT_SENS_DATA  = tuple(range(0x49,0x61))
MOT_DETECT_STATUS = 0x61
I2C_SLV0_DI    = 0x63
I2C_SLV1_DI    = 0x64
I2C_SLV2_DI    = 0x65
I2C_SLV3_DI    = 0x66
I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET  = 0x68
MOT_DETECT_CTRL = 0x69
USER_CTRL       = 0x6A
PWR_MGMT1       = 0x6B
PWR_MGMT2       = 0x6C
FIFO_COUNT_H    = 0x72
FIFO_COUNT_L    = 0x73
FIFO_R_W        = 0x74
WHO_AM_I        = 0x75

g = 9.81
temp = {'a':1/340, 'b':36.53}
GFS   = [250, 500, 1000, 2000]       #< Gyro range +/-(deg/s)
AFS   = [2, 4, 8, 16]                #< Acc range  +/-(g)
DLPF = [260, 184, 94, 44, 21, 10, 5] #< ACC BW (hz)
EXTSYNC = ['disable', 'temp', 'gx', 'gy', 'gz', 'ax', 'ay', 'az']
CLKSEL = ['int8Mhz', 'pllX', 'pllY', 'pllZ', '32.768Khz', '19.2Mhz', 'stop']
WU = [1.25, 5, 20, 40] #< Wake up rate
I2C_CLK = [348, 333, 320, 308, 296, 286, 276, 267,
           258, 500, 471, 444, 421, 400, 381, 364] #< I2C clock (Khz)

def accLsb(fs, g):
    """{0:16384/g, 1:8192/g, 2:4096/g, 3:2048/g]"""
    return g/(1<<(11 +3-fs))

def gyroLsb(fs):
    """{0:131 lsb/deg/s,    1:65.5 lsb/deg/s,   2:32.8 lsb/deg/s,   3:16.4 lsb/deg/s}"""
    """{0:2.2864 rad/s, 1:1.1432 lsb/rad/s, 2:0.5716 lsb/rad/s, 3:0.2858 lsb/rad/s}"""
    return 34.906 / (1<<(15 +3-fs)) #< Rad/sec/lsb
    #return 2000 / (1<<(15 +3-fs))  #< Deg/sec/lsb

class Reg8():
    size = 1
    name = "val"
    def __init__(self):
        self.val = 0

    def get(self) -> dict:
        return {self.name:self.val}

    def toBytes(self, val) -> list:
        return [0xff&val]
    
    def fromBytes(self, byte):
        self.val = byte&0xff
        return self

class Reg16(Reg8):
    size = 2
    def toBytes(self, val) -> list:
        val = int(val)
        msb = val>>8
        lsb = val&0xff
        return [msb, lsb]
    
    def fromBytes(self, vByte):
        self.val = vByte[0]*256 +vByte[1]
        return self

class RegS16(Reg16):
    def fromBytes(self, vByte):
        super().fromBytes(vByte)
        if self.val > 0x7FFF:
            self.val = -1*(((~self.val)+1)&0xffff)
        return self

class SelfTestX():
    ad   = SELF_TEST_X
    size = 1
    def __init__(self):
        self.gyro = 0
        self.acc  = 0

    def get(self) -> dict:
        return {"gx_test":self.gyro, "ax_test":self.acc}

    def toBytes(self, gyro, acc) -> list:
        gyro &= 0x1f
        accl &= 0x7
        return [(acc<<5) +gyro]
    
    def fromBytes(self, byte):
        self.gyro = byte&0x1f
        self.acc  = byte>>5
        return self
    
class SelfTestY(SelfTestX):
    ad   = SELF_TEST_Y
    def get(self) -> dict:
        return {"gy_test":self.gyro, "ay_test":self.gyro}

class SelfTestZ(SelfTestX):
    ad   = SELF_TEST_Z
    def get(self) -> dict:
        return {"gz_test":self.gyro, "az_test":self.gyro}

class SelfTestA():
    ad   = SELF_TEST_A
    size = 1
    def __init__(self):
        self.za = 0
        self.ya = 0
        self.xa = 0

    def get(self) -> dict:
        return {"za_test":self.za, "ya_test":self.ya, "xa_test":self.xa}

    def toBytes(self, xa, ya, za) -> list:
        xa &= 0x3
        ya &= 0x3
        za &= 0x3
        return [(xa<<4) +(ya<<2) +za]
    
    def fromBytes(self, byte):
        self.za = byte&0x3
        self.ya = (byte>>2)&0x3
        self.xa = (byte>>4)&0x3
        return self

class SamplerRateDiv(Reg8):
    ad   = SMPRT_DIV
    name = "smprt_div"

class Config():
    ad   = CONFIG
    size = 1
    def __init__(self):
        self.ext_sync_set = 0
        self.dlpf_hz     = DLPF[0]

    def get(self) -> dict:
        return {"ext_sync":self.ext_sync_set, "dlpf_hz":self.dlpf_hz}

    def toBytes(self, ext_sync=EXTSYNC[0], dlpf_hz=DLPF[0]) -> list:
        dlpf = DLPF.index(dlpf_hz)
        ext_sync_set = EXTSYNC.index(ext_sync) 
        return [(ext_sync_set<<3) +dlpf]
    
    def fromBytes(self, byte):
        self.dlpf_hz  = DLPF[0x7&byte]
        self.ext_sync = EXTSYNC[0x7&(byte>>3)]
        return self

class GyroConfig(Reg8):
    ad   = GYRO_CONFIG
    name = "fs_dps"

    def toBytes(self, fs_dps) -> list:
        fs_sel = GFS.index(fs_dps)
        return [fs_sel<<3]
    
    def fromBytes(self, byte):
        self.val = GFS[0x3&(byte>>3)]
        return self

class AccelConfig():
    ad   = ACCEL_CONFIG
    size = 1
    def __init__(self):
        self.xa_st = 0
        self.ya_st = 0
        self.za_st = 0
        self.afs_g = AFS[0]

    def get(self) -> dict:
        return {"afs_g":self.afs_g,
                "xa_st":self.xa_st,
                "ya_st":self.ya_st,
                "za_st":self.za_st}

    def toBytes(self, xa_st=0, ya_st=0, za_st=0, fs_g=AFS[0]) -> list:
        xa_st &= 1
        ya_st &= 1
        za_st &= 1
        fs_sel = AFS.index(fs_g)
        return [(xa_st<<7) +(xa_st<<6) +(xa_st<<5) +(fs_sel)<<3]
    
    def fromBytes(self, byte):
        self.xa_st = (byte>>7)
        self.ya_st = (byte>>6)&1
        self.za_st = (byte>>5)&1
        self.afs_g = AFS[(byte>>3)&3]
        return self

class FifoEn():
    ad   = FIFO_EN
    size = 1
    def __init__(self):
        self.temp_fifo_en  = 0
        self.xg_fifo_en    = 0
        self.yg_fifo_en    = 0
        self.zg_fifo_en    = 0
        self.accel_fifo_en = 0
        self.slv2_fifo_en  = 0
        self.slv1_fifo_en  = 0
        self.slv0_fifo_en  = 0

    def get(self) -> dict:
        return {"temp_fifo_en":self.temp_fifo_en,
                "xg_fifo_en":self.xg_fifo_en,
                "yg_fifo_en":self.yg_fifo_en,
                "zg_fifo_en":self.zg_fifo_en,
                "accel_fifo_en":self.accel_fifo_en,
                "slv2_fifo_en":self.slv2_fifo_en,
                "slv1_fifo_en":self.slv1_fifo_en,
                "slv0_fifo_en":self.slv0_fifo_en}

    def toBytes(self,
                accel_fifo_en=0,
                temp_fifo_en=0,
                xg_fifo_en=0,
                yg_fifo_en=0,
                zg_fifo_en=0,
                slv2_fifo_en=0,
                slv1_fifo_en=0,
                slv0_fifo_en=0) -> list:
        byte  = (temp_fifo_en&1)<<7
        byte += (xg_fifo_en&1)<<6
        byte += (yg_fifo_en&1)<<5
        byte += (zg_fifo_en&1)<<4
        byte += (accel_fifo_en&1)<<3
        byte += (slv2_fifo_en&1)<<2
        byte += (slv1_fifo_en&1)<<1
        byte += slv1_fifo_en
        return [byte]
    
    def fromBytes(self, byte):
        self.temp_fifo_en  = 1&(byte>>7)
        self.xg_fifo_en    = 1&(byte>>6)
        self.yg_fifo_en    = 1&(byte>>5)
        self.zg_fifo_en    = 1&(byte>>4)
        self.accel_fifo_en = 1&(byte>>3)
        self.slv2_fifo_en  = 1&(byte>>2)
        self.slv1_fifo_en  = 1&(byte>>1)
        self.slv0_fifo_en  = 1&byte
        return self

class InitPinCfg():
    ad   = INT_PIN_CFG
    size = 1
    def __init__(self):
        self.int_level = 0
        self.int_open  = 0
        self.latch_int_en  = 0
        self.init_rd_clear = 0
        self.fsync_init_level = 0
        self.fsync_init_en = 0
        self.i2c_bypass_en = 0

    def get(self) -> dict:
        return {"temp_fifo_en":self.temp_fifo_en,
                "xg_fifo_en":self.xg_fifo_en,
                "yg_fifo_en":self.yg_fifo_en,
                "zg_fifo_en":self.zg_fifo_en,
                "accel_fifo_en":self.accel_fifo_en,
                "slv2_fifo_en":self.slv2_fifo_en,
                "slv1_fifo_en":self.slv1_fifo_en,
                "slv0_fifo_en":self.slv0_fifo_en}

    def toBytes(self,
                int_level,
                int_open,
                latch_int_en,
                init_rd_clear,
                fsync_init_level,
                fsync_init_en,
                i2c_bypass_en) -> list:
        byte  = (int_level&1)<<7
        byte += (int_open&1)<<6
        byte += (latch_int_en&1)<<5
        byte += (init_rd_clear&1)<<4
        byte += (fsync_init_level&1)<<3
        byte += (fsync_init_en&1)<<2
        byte += (i2c_bypass_en&1)<<1
        return [byte]
    
    def fromBytes(self, byte):
        self.int_level        = 1&(byte>>7)
        self.int_open         = 1&(byte>>6)
        self.latch_int_en     = 1&(byte>>5)
        self.init_rd_clear    = 1&(byte>>4)
        self.fsync_init_level = 1&(byte>>3)
        self.fsync_init_en    = 1&(byte>>2)
        self.i2c_bypass_en    = 1&(byte>>1)
        return self

class IntEnable():
    ad   = INT_ENABLE
    size = 1
    def __init__(self):
        self.fifo_overflow_en = 0
        self.i2c_mst_int_en = 0
        self.data_rdy_en = 0

    def get(self) -> dict:
        return {"fifo_overflow_en":self.fifo_overflow_en,
                "i2c_mst_int_en":self.i2c_mst_int_en,
                "data_rdy_en":self.data_rdy_en}

    def toBytes(self,
                fifo_overflow_en=0,
                i2c_mst_int_en=0,
                data_rdy_en=0) -> list:
        byte  = (fifo_overflow_en&1)<<4
        byte += (i2c_mst_int_en&1)<<3
        byte += data_rdy_en&1
        return [byte]
    
    def fromBytes(self, byte):
        self.fifo_overflow_en = 1&(byte>>4)
        self.i2c_mst_int_en   = 1&(byte>>3)
        self.ata_rdy_en       = 1&byte
        return self

class IntStatus():
    ad   = INT_STATUS
    size = 1
    def __init__(self):
        self.fifo_overflow_int = 0
        self.i2c_mst_int_int = 0
        self.data_rdy_int = 0

    def get(self) -> dict:
        return {"fifo_overflow_int":self.fifo_overflow_int,
                "i2c_mst_int_int":self.i2c_mst_int_int,
                "data_rdy_int":self.data_rdy_int}

    def toBytes(self,
                fifo_overflow_int,
                i2c_mst_int_int,
                data_rdy_int) -> list:
        byte  = (fifo_overflow_int&1)<<4
        byte += (i2c_mst_int_int&1)<<3
        byte += data_rdy_int&1
        return [byte]
    
    def fromBytes(self, byte):
        self.fifo_overflow_int = 1&(byte>>4)
        self.i2c_mst_int_int   = 1&(byte>>3)
        self.ata_rdy_int       = 1&byte
        return self

class AccelXout(RegS16):
    ad   = ACCEL_XOUT_H
    name = "accel_xout"

class AccelYout(RegS16):
    ad   = ACCEL_YOUT_H
    name = "accel_yout"

class AccelZout(RegS16):
    ad   = ACCEL_ZOUT_H
    name = "accel_zout"

class TempOut(RegS16):
    ad   = TEMP_OUT_H
    name = "temp_out"

class GyroXout(RegS16):
    ad   = GYRO_XOUT_H
    name = "gyro_xout"

class GyroYout(RegS16):
    ad   = GYRO_YOUT_H
    name = "gyro_yout"

class GyroZout(RegS16):
    ad   = GYRO_XOUT_H
    name = "gyro_zout"

class SignalPathReset():
    ad   = SIGNAL_PATH_RESET
    size = 1
    def __init__(self):
        self.gyro = 0
        self.acc = 0
        self.temp = 0

    def get(self) -> dict:
        return {"gyro_reset":self.gyro,
                "accel_reset":self.acc,
                "temp_reset":self.temp}

    def toBytes(self, gyro_rst=1, acc_rst=1, temp_rst=1) -> list:
        byte  = (gyro_rst&1)<<2
        byte += (acc_rst&1)<<1
        byte += temp_rst&1
        return [byte]
    
    def fromBytes(self, byte):
        self.gyro = 1&(byte>>2)
        self.acc  = 1&(byte>>31)
        self.temp = 1&byte
        return self

class UserCtrl():
    ad   = USER_CTRL
    size = 1
    def __init__(self):
        self.fifo_en = 0
        self.i2c_mst_en = 0
        self.i2c_if_dis = 0
        self.fifo_rst = 0
        self.i2c_mst_rst = 0
        self.sig_cond_rst = 0

    def get(self) -> dict:
        return {"fifo_en":self.fifo_en,
                "i2c_mst_en":self.i2c_mst_en,
                "i2c_if_dis":self.i2c_if_dis,
                "fifo_rst":self.fifo_rst,
                "mst_rst":self.i2c_mst_rst,
                "sig_cond_rst":self.sig_cond_rst}

    def toBytes(self,
                fifo_en=0,
                i2c_mst_en=0,
                i2c_if_dis=0,
                fifo_rst=0,
                i2c_mst_rst=0,
                sig_cond_rst=0) -> list:
        byte  = (fifo_en&1)<<6
        byte += (i2c_mst_en&1)<<5
        byte += (i2c_if_dis&1)<<4
        byte += (fifo_rst&1)<<2
        byte += (i2c_mst_rst&1)<<1
        byte += sig_cond_rst&1
        return [byte]
    
    def fromBytes(self, byte):
        self.fifo_en    = 1&(byte>>6)
        self.i2c_mst_en = 1&(byte>>5)
        self.i2c_if_dis = 1&(byte>>4)
        self.fifo_rst = 1&(byte>>2)
        self.i2c_mst_rst = 1&(byte>>1)
        self.sig_cond_rst = 1&byte
        return self

class PwrMgmt1():
    ad   = PWR_MGMT1
    size = 1
    def __init__(self):
        self.device_rst = 0
        self.sleep      = 0
        self.cycle      = 0
        self.temp_dis   = 0
        self.clk        = 0

    def get(self) -> dict:
        return {"device_rst":self.device_rst,
                "sleep":self.sleep,
                "cycle":self.cycle,
                "temp_dis":self.temp_dis,
                "clk":self.clk}

    def toBytes(self, device_rst=0, sleep=0, cycle=0, temp_dis=0, clk=CLKSEL[1]) -> list:
        byte  = (device_rst&1)<<7
        byte += (sleep&1)<<6
        byte += (cycle&1)<<5
        byte += (temp_dis&1)<<3
        byte += CLKSEL.index(clk)
        return [byte]
    
    def fromBytes(self, byte):
        self.device_rst = 1&(byte>>7)
        self.sleep      = 1&(byte>>6)
        self.cycle      = 1&(byte>>5)
        self.temp_dis   = 1&(byte>>3)
        self.clk        = 7&byte
        return self

class PwrMgmt2():
    ad   = PWR_MGMT2
    size = 1
    def __init__(self):
        self.lp_wake_hz = 0
        self.stby_xa = 0
        self.stby_ya = 0
        self.stby_za = 0
        self.stby_xg = 0
        self.stby_yg = 0
        self.stby_zg = 0

    def get(self) -> dict:
        return {"lp_wake_hz":self.lp_wake_hz,
                "stby_xa":self.stby_xa,
                "stby_ya":self.stby_ya,
                "stby_za":self.stby_za,
                "stby_xg":self.stby_xg,
                "stby_yg":self.stby_yg,
                "stby_zg":self.stby_zg}

    def toBytes(self, lp_wake_hz,
                stby_xa, stby_ya, stby_za,
                stby_xg, stby_yg, stby_zg) -> list:
        byte  = WU.index(lp_wake_hz)<<6
        byte += (stby_xa&1)<<5
        byte += (stby_ya&1)<<4
        byte += (stby_za&1)<<3
        byte += (stby_xg&1)<<2
        byte += (stby_yg&1)<<1
        byte += (stby_zg&1)
        return [byte]
    
    def fromBytes(self, byte):
        self.lp_wake_hz = WU[3&(byte>>6)]
        self.stby_xa      = 1&(byte>>5)
        self.stby_ya      = 1&(byte>>4)
        self.stby_za      = 1&(byte>>3)
        self.stby_xg      = 1&(byte>>2)
        self.stby_yg      = 1&(byte>>1)
        self.stby_zg      = 1&(byte)
        return self

class FifoCount(Reg16):
    ad   = FIFO_COUNT_H
    name = "fifo_count"

class FifoRw(Reg8):
    ad   = FIFO_R_W
    name = "fifo_rw"

class WhoAmI(Reg8):
    ad   = WHO_AM_I
    name = "whoAmI"
