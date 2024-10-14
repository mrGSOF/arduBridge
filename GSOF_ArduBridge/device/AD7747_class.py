class AD7747():
    ### Registers map
    STATUS = 0x00

    CAPH = 0x01
    CAPM = 0x02
    CAPL = 0x03

    VTH = 0x04
    VTM = 0x05
    VTL = 0x06

    CAP_SETUP = 0x07
    VT_SETUP = 0x08
    EXC_SETUP = 0x09
    CONFIG = 0x0a

    CAP_DAC_A = 0x0b
    CAP_DAC_B = 0x0c

    CAP_OFS_H = 0x0d
    CAP_OFS_L = 0x0e

    CAP_GAIN_H = 0x0f
    CAP_GAIN_L = 0x10

    VOLT_OFS_H = 0x11
    VOLT_OFS_L = 0x12
    
    def __init__(self, i2c, dev=0x48):
        self.i2c = i2c
        self.dev = dev
        self.delay = 0.0
    
    def binToV(self, bin):
        return 1.17*(bin/2**24)

    def binToDegC(self, b):
        return (b/2048.0) -4096

    def binToCap(self, b):
        return b*(8.192/0x800000) -8.192

    def getAll(self):
        degC = 0.0
        cap = 0.0
        data = self.i2c.readRegister( dev=self.dev, reg=self.CAPH, N=6, delay=self.delay )
        #print(data)      #< For debug
        if len(data) > 5:
            cap = self.binToCap( (data[0]<<16) +(data[1]<<8) +data[2] )
            degC = self.binToDegC( (data[3]<<16) +(data[4]<<8) +data[5] )
        return (cap, degC)

    def getCap(self):
        cap = -32.0
        data = self.i2c.readRegister( dev=self.dev, reg=self.CAPH, N=3, delay=self.delay )
        #print(data)      #< For debug
        if len(data) > 2:
            cap = self.binToCap( (data[0]<<16) +(data[1]<<8) +data[2] )
        return cap

    def getVolt(self):
        volt = 0.0
        data = self.i2c.readRegister( dev=self.dev, reg=self.VTH, N=3, delay=self.delay )
        #print(data)      #< For debug
        if len(data) > 2:
            volt = (data[0]<<16) +(data[1]<<8) +data[2]
        return volt

    def getTemperature(self):
        return self.binToDegC( self.getVolt() )

    def getStatus(self):
        status = self.i2c.readRegister( dev=self.dev, reg=self.STATUS, N=1 )
        return status[0]

    def isReady(self):
        status = self.getStatus()
        if (status&0x4) == 0:
            return True
        return False

    def setDAC(self, ch, val):
        if val > 0:
            val |= 0x80
        else:
            val = 0
        self.i2c.writeRegister( dev=self.dev, reg=self.CAP_DAC_A +ch, vByte=[val] )

    def configure(self, dacA=0, dacB=0):
        cap = 0xa0
        vt = 0x81
        exc = 1<<3 | 1<<2 | 2  #< EXTDAC=1, EXCEN=1, EXCLVL=2
        cfg = 3<<6 | 6<<3 | 1  #< VTFS=8.2hz, CAPFS=5.5hz, continuous sampling
        self.i2c.writeRegister( dev=self.dev, reg=self.CAP_SETUP, vByte=[cap, vt, exc, cfg] )
        self.setDAC( 0, dacA )
        self.setDAC( 1, dacB )
