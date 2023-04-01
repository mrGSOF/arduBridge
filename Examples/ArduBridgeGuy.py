#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 11/Jule/2018
"""

#Basic modules to load
import time
from GSOF_ArduBridge import udpControl
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge import ArduBridge_HW #ArduShield class
from GSOF_ArduBridge import ElectrodeGpioStack
from GSOF_ArduBridge import threadPID_HW11 as threadPID
from GSOF_ArduBridge import UDP_Send

def extEval(s):
    s=str(s)
    print s
    eval(s)

def close():
    if udpConsol != False:
        udpConsol.active = False
    setup.stop()

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    import Guy_proto as protocol #<--Your experiment protocol file name
    port = 'COM6' #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2 #<--ArduBridge_V1.0 uses 115200 other versions use 230400 = 115200*2 
    ONLINE = False#True#False #<--True to enable work with real Arduino, False for simulation only.
    PID1 = False #<--True / False to build a PID controller.
    PID2 = False #<--True / False to build a PID controller.
    ELEC_EN = True #False #<--True to enable the real electrodes, False for simulation only.
    STACK_BUILD = [0x40,0x41,0x42,0x43,0x44,0x45]
    PORT_BASE = 7000 #7000
    REMOTE_CTRL_PORT = PORT_BASE +10 #-1
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    udpSendPid = UDP_Send.udpSend(nameID='', DesIP='127.0.0.1', DesPort=PORT_BASE +0)
    udpSendChip = UDP_Send.udpSend(nameID='', DesIP='127.0.0.1', DesPort=PORT_BASE +1)
    udpCamMgr = UDP_Send.udpSend(nameID='', DesIP='127.0.0.1', DesPort=PORT_BASE +3)
    udpConsol = False
    if REMOTE_CTRL_PORT > 1:
        udpConsol = udpControl.udpControl(nameID='udpIDLE', RxPort=REMOTE_CTRL_PORT, callFunc=extEval)
        print 'Remote-Consol-Active on port %s\n'%(str(REMOTE_CTRL_PORT))
    print 'Using port %s at %d'%(port, baudRate)
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate )
    if ONLINE:
        ardu.OpenClosePort(1)
        print 'Connecting to Arduino ON-LINE.'
    else:
        print 'Arduino OFF-LINE. Simulation mode'

    ExtGpio = ElectrodeGpioStack.ExtGpioStack(i2c=ardu.i2c, devList=STACK_BUILD, v=False)#True)
    ExtGpio.init()
    ExtGpio.init()
    ardu.Reset()
    print 'Ready...\n'

    if PID1 == True:
        PID = threadPID.ArduPidThread(bridge=ardu,
                                      nameID='PID1',       # Process name
                                      Period=0.5,          # The PID calculation cycle-time
                                      fbPin=0,             # The analog pin of the temperture sensor
                                      outFunc=hw.pwmA,     # The PWM output to the H-Bridge
                                      viewer={'UDP1': udpSendPid1.Send}
                                      )
        PID.PID.Kp = 10.0
        PID.PID.Ki = 1.0
        PID.PID.Kd = 0.0
        PID.enOut = True
        hw.pwmA_init()
        print 'type PID.start() to start the PID thread\n'

    if PID2 == True:
        PID2 = threadPID.ArduPidThread(bridge=ardu,
                                      nameID='PID2',
                                      Period=0.5,          # The PID calculation cycle-time
                                      fbPin=1,             # The analog pin of the temperture sensor
                                      outFunc=hw.pwmB,     # The PWM output to the H-Bridge
                                      viewer={'UDP2': udpSendPid2.Send}
                                      )
        PID2.PID.Kp = 10
        PID2.PID.Ki = 1.0
        PID2.PID.Kd = 0.0
        PID2.enOut = True
        hw.pwmB_init()
        print 'type PID2.start() to start the PID2 thread\n'

    setup = protocol.Setup(ExtGpio=ExtGpio, gpio=ardu.gpio, chipViewer=udpSendChip.Send)
    setup.enOut(ELEC_EN)
