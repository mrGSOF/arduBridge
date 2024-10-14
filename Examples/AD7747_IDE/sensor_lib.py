from GSOF_ArduBridge.device import AD7747_class

class conv():
    def __init__(self, gain=0.0, offset=0.0):
        self.offset = offset
        self.gain = gain
        self.val = 0.0

    def calc(self, val):
        self.val = self.gain*(val -self.offset)
        return self.val
    
class poly():
    def __init__(self, coef=(0.0, 0.0, 0.0), offset=0.0):
        self.offset = offset
        self.coef = coef
        self.val = 0.0

    def calc(self, val):
        val -= self.offset
        r = 0
        n = len(self.coef) -1
        for c in self.coef:
            r += c*(val)**n
        self.val = r
        return self.val

class CapSensor(AD7747_class.AD7747):
    def __init__(self, i2c, dev=0x48, units='psi', coef=(1,0), offset=0.0, temp=0.0, tcGain=0.0):
        super().__init__(i2c, dev)
        self.units = units
        
        self.pres = poly(coef,    #< (PSI / pF)
                         offset)  #< (pF)

        self.tc = conv(tcGain,    #< (pF / degC)
                       temp)      #< (degC)
    
    def barToPa(self, bar):
        return 100000*bar

    def paToInHg(self, pa):
        return 0.000295299*pa
    
    def paToPsi(self, pa):
        return 0.0001450377*pa

    def inHgToPa(self, inHg):
        return inHg/0.000295299

    def psiToPa(self, psi):
        return psi/0.0001450377

    def cToF(self, c):
        return c*1.8 +32.0

    def fToC(self, f):
        return (f -32.0)/1.8

    def unitsToPa(self, val, units=None):
        if units == None:
            units = self.units
        if units == 'psi':
            return self.psiToPa(val)
        elif units[0] == 'i':
            return self.inHgToPa(val)
        elif units == 'pa':
            return val
        else:
            print('Wrong pressure units')
            return val

    def paToUnits(self, pa, units=None):
        if units == None:
            units = self.units
        if units == 'psi':
            return self.paToPsi(pa)
        elif units[0] == 'i':
            return self.paToInHg(pa)
        elif units == 'pa':
            return pa
        elif units == 'bar':
            return pa/100000
        else:
            print('Wrong pressure units')
            return pa

    def capToPa(self, pF):
        return self.pres.calc(pF)
    
    def configure(self, dacA=28, dacB=0):
        super().configure(dacA, dacB)

    def getAll(self, temp=None, units=None):
        pF, degC = super().getAll()
        if temp == None:
            temp = degC
            
        pres = self.getPressure(pF=pF, temp=temp, units=units)
        return (pres, degC, self.pF)

    def setZero(self, pF=None, degC=None, N=8):
        if (pF == None) or (degC == None):
            sum_pF = 0
            sum_degC = 0
            for i in range(0,N):
                while self.isReady() == False:
                    print(".", end='')
                print('.')
                pa, degC, pF = self.getAll(temp=False, units="pa")
                sum_pF += pF
                sum_degC += degC
            self.pres.offset = sum_pF/N
            self.tc.offset = sum_degC/N
        else:
            self.pres.offset = pF
            self.tc.offset = degC
        return {"pF":self.pres.offset, "degC":self.tc.offset}

    def getPressure(self, pF=None, temp=None, units=None):
        self.tc.val = 0
        if temp != False:
            if temp == None:
                temp = self.getTemperature()
            self.tc.calc(temp)
            
        if pF == None:
            pF = self.getCap()
        pF -= self.tc.val
        self.pF = pF
        pa = self.capToPa(pF)
        return self.paToUnits(pa, units)
