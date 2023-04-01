import time

class chip104_ARRAY():
    def __init__(self, setup):
        self.setup = setup
        Map={
        '0x0' : 1,
        '0x1' : 25,
        '1x0' : 2,
        '1x1' : 26,
        '2x0' : 3,
        '2x1' : 27,
        '3x0' : 4,
        '3x1' : 28,
        '4x0' : 5,
        '4x1' : 29,
        '5x0' : 6,
        '5x1' : 30,
        '6x0' : 7,
        '6x1' : 31,
        '7x0' : 8,
        '7x1' : 32,
        '8x0' : 9,
        '8x1' : 33,
        '9x0' : 10,
        '9x1' : 34,
        '0x2' : 11,
        '0x3' : 35,
        '1x2' : 12,
        '1x3' : 36,
        '2x2' : 13,
        '2x3' : 37,
        '3x2' : 14,
        '3x3' : 38,
        '4x2' : 15,
        '4x3' : 39,
        '5x2' : 16,
        '5x3' : 40,
        '6x2' : 17,
        '6x3' : 41,
        '7x2' : 18,
        '7x3' : 42,
        '8x2' : 19,
        '8x3' : 43,
        '9x2' : 20,
        '9x3' : 44,
        'RES2C' : 21,
        'RES2B' : 45,
        'RES2A' : 22,
        'RES1D' : 46,
        'RES1C' : 23,
        'RES1B' : 47,
        'RES1A' : 24,

        'RES2D' : 48,
        'RES3A' : 49,
        'RES3B' : 50,
        'RES3C' : 51,
        'RES3D' : 52,
        'RES4A' : 53,
        'RES4B' : 54,
        'RES4C' : 55,
        'RES4D' : 56,
        'RES5A' : 57,

        '0x6' : 58,
        '0x5' : 82,
        '1x6' : 59,
        '1x5' : 83,
        '2x6' : 60,
        '2x5' : 84,
        '3x6' : 61,
        '3x5' : 85,
        '4x6' : 62,
        '4x5' : 86,
        '5x6' : 63,
        '5x5' : 87,
        '6x6' : 64,
        '6x5' : 88,
        '7x6' : 65,
        '7x5' : 89,
        '8x6' : 66,
        '8x5' : 90,
        '9x6' : 67,
        '9x5' : 91,
        '0x4' : 68,
        'RES5B' : 92,
        '1x4' : 69,
        'RES5C' : 93,
        '2x4' : 70,
        'RES5D' : 94,
        '3x4' : 71,
        'RES6A' : 95,
        '4x4' : 72,
        'RES6B' : 96,
        '5x4' : 73,
        'RES6C' : 97,
        '6x4' : 74,
        'RES6D' : 98,
        '7x4' : 75,
        'RES7A' : 99,
        '8x4' : 76,
        'RES7B' : 100,
        '9x4' : 77,
        'RES7C' : 101,
        'RES8A' : 78,
        'RES7D' : 102,
        'RES8B' : 79,
        'SPARE103' : 103,
        'RES8C' : 80,
        'SPARE104' : 104,
        'RES8D' : 81,
        }

        self.array=[
            [i for i in range(1,11)],  #row1
            [i for i in range(25,35)], #row2
            [i for i in range(11,21)], #row3
            [i for i in range(35,45)], #row4
            [i for i in range(68,78)], #row5
            [i for i in range(82,92)], #row6
            [i for i in range(58,68)], #row7
            ]

    def genArrayTestList(self, Min=(0,0), Max=(9,6)):
        minX = Min[0]
        minY = Min[1]
        maxX = Max[0]
        maxY = Max[1]
        elecList = []
        rightToLeft = True
        for row in range(minY,maxY +1):
            if rightToLeft:
                elecList += self.genTrackList( (minX,row),(maxX,row) )
                rightToLeft = False
                print '+%d'%row
            else:
                elecList += self.genTrackList( (maxX,row),(minX,row) )
                rightToLeft = True
                print '-%d'%row
        return elecList

    def arrayTest(self, Min=(0,0), Max=(9,6)):
        testList = self.genArrayTestList(Min, Max)
        if len(testList) > 0:
            self.setup.startSeq( testList, Period=0.8, onTime=0.8-0.2)
        print 'Testing the chip-array'
        
    def genDispList(self, res):
        resElec=[
            [55,56,1],
            [51,52,6],
            [45,22,10],
            [80,81,67],
            [101,102,63],
            [97,98,58],
            ]
        if (res <= resElec) and (res>0):
            dispList = []
            elec = resElec[res -1]
            dispList.append( [elec[0]] )
            dispList.append( [elec[0], elec[1]] )
            dispList.append( [elec[1], elec[2]] )
            dispList.append( [elec[0], elec[2]] )
            return dispList
        else:
            print 'Res out of range'
            return []

##    def genTrackList(self, src, des):
##        srcX = src[0]
##        srcY = src[1]
##        desX = des[0]
##        desY = des[1]
##        
##        elecList=[]
##        direction = (desX-srcX+1)/abs(desX-srcX+1)
##        for x in range(srcX, desX +direction,direction):
##            elecList.append(self.array[srcY][x])
##            
##        direction = (desY-srcY+1)/abs(desY-srcY+1)
##        for y in range(srcY +direction, desY +direction, direction):
##            elecList.append(self.array[y][desX])
##        return elecList

    def genTrackList(self, src, des, dim=(1,1)):
        srcX = src[0]
        srcY = src[1]
        desX = des[0]
        desY = des[1]
        dimX = dim[0]
        dimY = dim[1]
        
        elecList=[]
        directionX = (desX-srcX+1)/abs(desX-srcX+1)
        directionY = (desY-srcY+1)/abs(desY-srcY+1)

        for x in range(srcX, desX +directionX,directionX):
            elec = self.fillRec(topLeft=(x, srcY), dim=dim)
            elecList.append(elec)

        for y in range(srcY +directionY, desY +directionY, directionY):
            elec = self.fillRec(topLeft=(x, y), dim=dim)
            elecList.append(elec)
        return elecList

    def fillRec(self, topLeft, dim):
        srcX = topLeft[0]
        srcY = topLeft[1]
        dimX = dim[0]
        dimY = dim[1]

        elec = []
        for y in range(srcY, srcY +dimY):
            for x in range(srcX,srcX +dimX):
                elec.append(self.array[y][x])
        return elec        
        
    def genMixList(self, src, dx, dy, dim=(1,1)):
        srcX = src[0]
        srcY = src[1]
        
        elecList=[]
        for x in range(srcX, srcX +dx):
            elec = self.fillRec(topLeft=(x, srcY), dim=dim)
            elecList.append(elec)
#            elecList.append(self.array[srcY][x])
                            
        for y in range(srcY, srcY +dy):
            elec = self.fillRec(topLeft=(srcX +dx, y), dim=dim)
            elecList.append(elec)
#            elecList.append(self.array[y][srcX +dx])

        for x in range(srcX +dx, srcX, -1):
            elec = self.fillRec(topLeft=(x, srcY +dy), dim=dim)
            elecList.append(elec)
#            elecList.append(self.array[srcY +dy][x])

        for y in range(srcY +dy, srcY -1, -1):
            elec = self.fillRec(topLeft=(srcX, y), dim=dim)
            elecList.append(elec)
#            elecList.append(self.array[y][srcX])

        return elecList

    def track(self, src, des, dim=(1,1), T=0.8):
        trackList = self.genTrackList(src, des, dim)
        if len(trackList) > 0:
            self.setup.startSeq( trackList, Period=T, onTime=T-0.2)
            
    def mix(self, src=(0,0), x=1, y=1, dim=(1,1), N=1, T=0.8):
        mixList = self.genMixList(src, x, y, dim)
        if len(mixList) > 0:
            self.setup.startSeq( mixList, Period=T, onTime=T-0.2, N=N)

    def disp(self, res, dly=0.7):
        resElec=[
            [55,56,1],
            [51,52,6],
            [45,22,10],
            [80,81,67],
            [101,102,63],
            [97,98,58],
            ]
        if (res <= resElec) and (res>0):
            ON = 1
            OFF = 0
            ExtGpio = self.setup.ExtGpio
            elec = resElec[res -1]
            ExtGpio.pinWrite(elec[0],ON)
            time.sleep(dly)
            ExtGpio.pinWrite(elec[1],ON)
            time.sleep(dly)
            ExtGpio.pinWrite(elec[0],OFF)
            ExtGpio.pinWrite(elec[2],ON)
            time.sleep(dly)
            ExtGpio.pinWrite(elec[1],OFF)
            ExtGpio.pinWrite(elec[0],ON)
            time.sleep(dly)
            ExtGpio.pinWrite(elec[0],OFF)
            ExtGpio.pinWrite(elec[1],OFF)
            ExtGpio.pinWrite(elec[2],OFF)
        else:
            print 'Res out of range'

    def impedanceCheck(elec):
        ON = 1
        OFF = 0
        ExtGpio = self.setup.ExtGpio
        elec = self.array[y][x]
        ExtGpio.pinWrite(elec, ON)
        cur = self.setup.hw.chipCurrectSample()
        ExtGpio.pinWrite(elec, OFF)
        return cur

    def impedanceScan(topLeft=(0,0), botRight=(9,6)):
        ON = 1
        OFF = 0
        for y in range(topLeft[1],botRight[1]):
            for x in range(topLeft[0],botRight[0]):
                self.impMap[y][x] = self.impedanceCheck(self.array[y][x])
                
