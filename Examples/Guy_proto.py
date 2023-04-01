""" 
If ERRs at start,
ExtGpio.init()
"""

try:
    from GSOF_ArduBridge import threadElectrodeSeq
except ImportError:
    threadElectrodeSeq = False
    class dummyThread():
        def __init__(self, nameID):
            self.name = nameID

import time
import Chip104_Array as chip

class Setup():
    def __init__(self, ExtGpio, gpio, chipViewer):
        self.gpio = gpio
        self.ExtGpio = ExtGpio
        self.chipViewer = chipViewer
        self.chip = chip.chip104_ARRAY(self)

        self.seq = {} #initializes dictionary, which is an array of associations; returns associated value when a value is inputted
        self.categoryDict = {}

        self.genSeq = []
##        self.genSeq.append(threadElectrodeSeq.MoveElecSeqThread(gpio=ExtGpio,
##                                                                nameID='genSeq1', #The name of the protocol
##                                                                Period=1.0, #Total time [Sec]
##                                                                onTime=0.7, #On time for each electrod [Sec]
##                                                                elecList=[] #The list itself
##                                                                )
##                           )
##        self.genSeq[-1].addViewer('UDP', chipViewer)
        
#####################################################DISPENSING RELATED#######################################
        for i in range(1,7):
            # \/ ** START OF SEQUENCE ** \/
            seqCategory = 'Dispensing'  #<-- EDIT THIS
            seqName = 'dispT%d'%i  #<-- EDIT THIS
            seqDesc = 'Dispense to small electrode from the top 1st reservoir.'  #<-- EDIT THIS
            seqList = self.chip.genDispList(i) # <-- Electrodes
            seqPeriod=0.8 # <-- Keep this at least 0.2 seconds above onTime [Sec]
            seqOnTime=seqPeriod -0.2 # <-- How long is the electrode actuated [Sec]
            self.seqAdd(seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer) #DON'T EDIT
            # /\ **  END OF SEQUENCE  ** /\

        # \/ ** START OF SEQUENCE ** \/
##        seqCategory = 'Dispensing'  #<-- EDIT THIS
##        seqName = 'dispT6'  #<-- EDIT THIS
##        seqDesc = 'Dispense to small electrode from the top 1st reservoir.'  #<-- EDIT THIS
##        seqList = self.genDispList(6) # <-- Electrodes
##        seqOnTime=0.7 # <-- How long is the electrode actuated [Sec]
##        seqPeriod=1 # <-- Keep this at least 0.2 seconds above onTime [Sec]
##        self.seqAdd(seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer) #DON'T EDIT
        # /\ **  END OF SEQUENCE  ** /\


    def catAdd(self, catName):
        if not catName in self.categoryDict.keys():
            self.categoryDict[catName] = [] #initializes list for each category
        
    def seqAdd(self, seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer):
        if threadElectrodeSeq == False:
            self.seq[seqName] = dummyThread(seqName)
        else:
            self.seq[seqName] = threadElectrodeSeq.ArduElecSeqThread(gpio=ExtGpio,
                                                        nameID=seqName,
                                                        Period=seqPeriod,
                                                        onTime=seqOnTime,
                                                        elecList= seqList
                                                        )
            self.seq[seqName].addViewer('UDP', chipViewer)
        self.seq[seqName].desc = seqDesc
        self.catAdd(seqCategory)
        self.categoryDict[seqCategory].append(seqName)

    def seqPrint(self, val=True):
        for seqName in self.seqDesc.keys():
            print '%s -> %s'%(seqName, self.seqDesc[seqName]) 

    def enOut(self, val=True):
        for seqName in self.seq.keys():
            self.seq[seqName].enOut = val

    def stop(self):
        for seqName in self.seq.keys():
            self.seq[seqName].stop()
        
    def startSeq(self, elecList, N=1, onTime=0.7, Period=1.0, moveSeq=False):
        freeSeq = False
        for seq in self.genSeq:
            if seq.enable == False:
                freeSeq = seq
        if freeSeq == False:
            seqName = 'genSeq%d'%(len(self.genSeq)+1)
            print 'Building new genSeq %s'%(seqName)
            if moveSeq == True:
                print 'Move'
                self.genSeq.append(threadElectrodeSeq.MoveElecSeqThread(gpio=self.ExtGpio,
                                                                        nameID=seqName, #The name of the protocol
                                                                        Period=Period, #Total time [Sec]
                                                                        onTime=onTime, #On time for each electrod [Sec]
                                                                        elecList=elecList #The list itself
                                                                        )
                                   )
            else:
                print 'Sequence'
                self.genSeq.append(threadElectrodeSeq.ArduElecSeqThread(gpio=self.ExtGpio,
                                                                        nameID=seqName, #The name of the protocol
                                                                        Period=Period, #Total time [Sec]
                                                                        onTime=onTime, #On time for each electrod [Sec]
                                                                        elecList=elecList #The list itself
                                                                        )
                                   )

            freeSeq = self.genSeq[-1]
            freeSeq.enOut = True

            freeSeq.addViewer('UDP', self.chipViewer)
        else:
            print 'Using %s'%(freeSeq.name)
            freeSeq.Period=Period #Total time [Sec]
            freeSeq.onTime=onTime #On time for each electrod [Sec]
            freeSeq.elecList=elecList #The list itself
        freeSeq.start(N)
        return freeSeq
