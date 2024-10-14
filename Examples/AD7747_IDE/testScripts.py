#!/usr/bin/env python
"""
By: Guy Soffer
Date: 01/Apr/2021
"""

import time, statistics

class accuracy():
    def __init__(self, targetPos):
        self.trg = targetPos
        self.meas = []
        self.avg = 0
        self.stdev = 0    

    def addMeas(self, pos):
        self.meas.append(pos)
        
    def calcAvg(self):
        self.avg = sum(self.avg)/len(self.avg)
        return self.avg

    def calcStdev(self):
        self.stdev = statistics.stdev(self.meas)
        return self.stdev

class movAvg():
    def __init__(self, taps=8, initVal=1):
        #self.N = taps
        self.buf = [initVal]*taps

    def filter(self, val):
        self.buf.pop(0)
        self.buf.append(val)
        return sum(self.buf)/len(self.buf)

class test():
    def __init__(self, sns, units='psi'):
        self.sns = sns
        self.units = units
        #self.printHelp()
        
    def printHelp(self):
        print( "sns.configure()" )
        print( "sns.setZero()" )
        print( "test.sample('psi', DT=10, N=-1)" )

    def config(self):
        self.sns.configure()

    def sample(self, units="psi", DT=0.5, N=-1):
        n = N
        if N == -1:
            n = 1
            
        flt = movAvg(taps=8, initVal=self.sns.getPressure(units=units))
        T0 = time.time()
        Tnext = time.time() -T0 +DT
        while (n > 0):
            pres, degC, pF = self.sns.getAll(units=units)
            pF_tc = self.sns.tc.val
            #pres = flt.filter( self.sns.getPressure(units=units) )
            print( "%3.1f,%1.5f,%1.5f,%1.5f,%1.5f,"%(time.time() -T0, pres, degC, pF, pF_tc) )
            while ( (time.time() -T0) < Tnext):
                time.sleep(DT/10)
            Tnext += DT
            if N != -1:
                n -= 1
