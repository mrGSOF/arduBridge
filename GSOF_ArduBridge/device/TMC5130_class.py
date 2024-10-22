
from GSOF_ArduBridge.ArduSPI import csLow, csHigh

class TMC5130():
    ### Registers map
    GCONF = 0x00
    GSTAT = 0x01
    IFCNT = 0x02
    SLAVECONF = 0x03
    IOIN = 0x04
    OUTPUT = 0x04
    X_COMPARE = 0x05

    IHOLD_IRUN = 0x10
    TPOWERDOWN = 0x11
    TSTEP = 0x12
    TPWMTHRS = 0x13
    TCOOLTHRS = 0x14
    THIGH = 0x15

    RAMPMODE = 0x20
    XACTUAL = 0x21
    VACTUAL = 0x22
    VSTART = 0x23
    A1 = 0x24
    V1 = 0x25
    AMAX = 0x26
    VMAX = 0x27
    DMAX = 0x28
    D1 = 0x2A
    VSTOP = 0x2B
    TZEROWAIT = 0x2C
    XTARGET = 0x2D

    VDCMIN = 0x33
    SW_MODE = 0x34
    RAMP_STAT = 0x35
    XLATCH = 0x36

    CHOPCONF = 0x6c
    COOLCONF = 0x6d
    DCCTRL = 0x6e
    DRV_STATUS = 0x6f
    PWMCONF = 0x70
    PWM_SCALE = 0x71
    ENCM_CTRL = 0x72
    LOST_STEPS = 0x73
    pi = 3.141592653589793 #< Inorder not to include the math library

    def __init__(self, cs, out, stepSizeDeg=0.9):
        self.cs  = cs
        self.wr  = out
        self.holdCurrent = 0
        self.runCurrent  = 0
        self.holdDelay   = 0
        self.maxCurrent  = 1500
        self.microSteps  = 256
        self.stepperStepSizeDeg = stepSizeDeg
        self.calcStepSize()
        self.units = 'deg'
        self.timeScale = 3.0
        self.noCross = None

    def calcStepSize(self):
        self.stepsRev = self.microSteps*360/self.stepperStepSizeDeg
        self.stepDeg = 360/self.stepsRev
        self.stepRad = 2*self.pi/self.stepsRev

    def degToSteps(self, deg):
        return int(deg/self.stepDeg +0.5)
    
    def stepsToDeg(self, steps):
        return steps*self.stepDeg

    def radToSteps(self, rad):
        return int(rad/self.stepRad +0.5)

    def stepsToRad(self, steps):
        return steps*self.stepRad

    def unitsToSteps(self, val, units=False):
        if units == False:
            units = self.units
        if units[0] == 'd':
            return self.degToSteps(val)
        elif units[0] == 'r':
            return self.radToSteps(val)
        elif units[0] == 's' or units[0] == 'b':
            return val
        else:
            print('Wrong degrees units')
            return val

    def stepsToUnits(self, steps, units=False):
        if units == False:
            units = self.units
        if units[0] == 'd':
            return self.stepsToDeg(steps)
        elif units[0] == 'r':
            return self.stepsToRad(steps)
        elif units[0] == 's':
            return steps
        else:
            print('Wrong degrees units')
            return steps

    def rwN(self, addr, vDat):
        #self.cs(0)
        vDat = [addr]+vDat
        N = len(vDat)
        cs = self.cs.pin
        res = self.wr(cs1=csLow(cs), cs2=csHigh(cs), N=N, vByte=vDat) #< Addr, data
        res = res[1]
        #self.cs(1)
        return res

    def readStatus(self):
        return self.rwN(0x00, [])

    def read32bit(self, addr):
        N = 4
        res = self.rwN(addr&0x7f, [0xf0]*N) #< Set write bit to 0
        status = res.pop(0)
        val = 0
        for n in range(0,N):
            val += res[n]*256**(N-1-n)
        return (status, val)

    def write32bit(self, addr, dat):
        N = 4
        vDat = [0]*N
        for i in range(0,N):
            vDat[N-1-i] = dat&0xff
            dat = dat>>8
        
        res = self.rwN(0x80 | (addr&0x7f), vDat) #< Set write bit to 1
        status = res.pop(0)
        val = 0
        for n in range(0,N):
            val += res[n]*256**(N-1-n)
        return (status, val)

    def crcCalc(self, vBytes):
        crc = 0;
        for currentByte in vBytes: # Execute for all bytes of a message
            for j in range(0,8,1):  # Go over all the bits in the byte
                if (crc>>7)^(currentByte&0x01): # update CRC based result of XOR operation
                    crc = (crc<<1) ^ 0x07;
                else:
                    crc = (crc<<1);
                currentByte = currentByte >> 1;
        return crc

    def getRampStatus(self):
        return (self.read32bit(self.RAMP_STAT))[1]

    def isPosMatch(self): #< *** NOT RELIABLE ***
        #status, val = self.read32bit(self.RAMP_STAT)
        #status, val = self.read32bit(self.XACTUAL)
        status = (self.readStatus())[0]
        return status&0x20 #< Should work on paper
        #return self.getRampStatus()&0x200 #< Should work on paper

    def genIHOLD_IRUN_DELAY(self):
        ihold = int(31*(self.holdCurrent/self.maxCurrent))&0x1f
        irun = int(31*(self.runCurrent/self.maxCurrent))&0x1f
        val = (self.holdDelay<<16) +(irun<<8) +ihold
        print("%d, %d, %d"%(ihold, irun, self.holdDelay))
        return val
    
    def setRunCurrent(self, mA, v=False):
        if mA <= self.maxCurrent:
            self.runCurrent = mA
            val = self.genIHOLD_IRUN_DELAY()
            self.write32bit(self.IHOLD_IRUN, val)
            if v:
                print("Run current set to %d mA"%(mA))
        else:
            print("Error - over current (%d mA)"%(self.maxCurrent))

    def getRunCurrent(self):
        return self.runCurrent

    def setHoldCurrent(self, mA, v=False):
        if mA <= self.maxCurrent:
            self.holdCurrent = mA
            val = self.genIHOLD_IRUN_DELAY()
            self.write32bit(self.IHOLD_IRUN, val)
            if v:
                print("Hold current set to %d mA"%(mA))
        else:
            print("Error - over current (%d mA)"%(self.maxCurrent))

    def getHoldCurrent(self):
        return self.holdCurrent

    def setHoldDelay(self, clocks):
        if clocks < 2**16:
            self.delay = int(clocks)
            val = self.genIHOLD_IRUN_DELAY()
            self.write32bit(self.IHOLD_IRUN, val)
        else:
            print("Error - clocks over %d"%((2**16)-1))

    def setMaxVel(self, maxVel):
        self.write32bit(self.VMAX, int(maxVel))

    def setVSTOP(self, vel):
        self.write32bit(self.VSTOP, int(vel))

    def setMode(self, mode):
        if type(mode) == str:
            modeMap = {'POS':0, 'PVEL':1, 'NVEL':2, 'HOLD':3}
            if mode in modeMap:
                self.write32bit(self.RAMPMODE, modeMap[mode])
            else:
                print("Error - wrong control mode name")
        else:
            if mode < 3:
                self.write32bit(self.RAMPMODE, mode)
            else:
                print("Error - wrong control mode number")

    def setResolution(self, ms):
        print("Error - changing microstep value is not supported")

    def setActual(self, pos=0, units=False):
        steps = self.unitsToSteps(pos, units)
        self.write32bit(self.XACTUAL, steps)

    def resetPosition(self, pos=0, units=False, v=False):
        oldPos = self.getPosition('steps')
        trgPos = self.unitsToSteps(pos, units)
        while trgPos != oldPos:
            dStep = trgPos - oldPos
            if dStep > 1000:
                dStep = 1000
            elif dStep < -1000:
                dStep = -1000
            oldPos += dStep   
            self.write32bit(self.XACTUAL, oldPos)
            self.setPosition(oldPos, 'step')
        if v:
            print('Curret position was set to %d %s'%(pos, units))

    def setAccl(self, acc, units=False, v=False):
        stepsAcc = int(self.unitsToSteps(acc, units)*self.timeScale)
        self.write32bit(self.AMAX, 5*stepsAcc)
        self.write32bit(self.DMAX, 5*stepsAcc)
        if v:
            print('Acceleration set to %d %s / DT^2 (%d steps)'%(acc, units, stepsAcc))

    def setVelocity(self, vel, units=False, v=False):
        stepsVel = int(self.unitsToSteps(vel, units)*self.timeScale)
        self.write32bit(self.VMAX, stepsVel)
        if v:
            print('Velocity set to %d %s / DT (%d steps)'%(vel, units, stepsVel))

    def setNoCross(self, noCross, units=False):
        if noCross != None:
            noCross = self.unitsToSteps(noCross, units)
            if noCross < 0:
                maxRotation = self.unitsToSteps(360, 'deg')
                noCross = maxRotation + noCross
        self.noCross = noCross

    def getNoCross(self, units=False):
        noCross = self.noCross
        if noCross != None:
            return self.stepsToUnits( self.noCross, units )
        return noCross
    
    def checkNoCross(self, steps):
        if self.noCross != None:
            hyst = self.unitsToSteps(5, 'deg')
            maxRotation = self.unitsToSteps(360, 'deg')
            steps = steps%maxRotation
            #pos = self.stepsToUnits(steps, 'deg')
            if steps > 0:
                if steps > (self.noCross +hyst):
                    #print("position passed no-cross limit %d"%(pos))
                    steps = steps-maxRotation
            else:
                if steps < (self.noCross -maxRotation -hyst):
                    #print("position passed no-cross limit %d"%(pos))
                    steps = maxRotation +steps
        return steps

    def setPosition(self, pos, units=False, v=False):
        steps = self.unitsToSteps(pos, units)
        steps = self.checkNoCross(steps) ##< Make sure not to cross the self.noCross point
        self.write32bit(self.XTARGET, steps)
        if v:
            print('Curret position was set to %d %s (%d steps)'%(pos, units, steps))

    def getPosition(self, units=False):
        #pos = self.read32bit(self.XACTUAL)
        pos = self.read32bit(self.XACTUAL)
        pos = pos[1]
        ### If needed, convert the value to negative
        if pos > 0x80000000:
            pos ^= 0xffffffff
            pos += 1
            pos *= -1
        return self.stepsToUnits( pos, units )

    def configure(self):
        self.setHoldCurrent(mA=50, v=True)
        self.setRunCurrent(mA=300, v=True)
        
        self.write32bit(self.TPWMTHRS, 0x000001F4)
        
        self.write32bit(self.VSTART, 10)   #< Minimum pulse rate for first velocity (steps)
        self.write32bit(self.VSTOP, 10)    #< Minimum pulse rate before complete stop (steps)
        
        self.write32bit(self.A1, 16000)     #< First acceleration until V1 (steps)
        self.write32bit(self.D1, 16000)     #< Final decceleration from V2 (steps)
        self.write32bit(self.V1, 0)        #< A1/D1 to AMAX/DMAX velocity threshold. 0 to use only AMAX/DMAX

        #self.setAccl()
        self.write32bit(self.AMAX, 8000)   #< Second acceleration from V1 to VMAX (steps)
        self.write32bit(self.DMAX, 8000)   #< First decceleration from VMAX to V1 (steps)

        #self.setVelocity()
        self.write32bit(self.VMAX, 400000) #< Maximum pulse rate (steps)
        
        self.write32bit(self.CHOPCONF, 0x100c3)
