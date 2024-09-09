#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 19/Feb/2024
"""

#Basic modules to load
import time
from GSOF_ArduBridge import udpControl                   #< To control the movement of droplets by UDP commands
from GSOF_ArduBridge import ArduBridge                   #< The communication stack
from GSOF_ArduBridge import ArduBridge_HW                #< ArduShield class
from GSOF_ArduBridge import ElectrodeGpioStack           #< Stack of multiple electrode-driver boards
from GSOF_ArduBridge import pca9505_class as PCA9505     #< PCA9505 port extender
from GSOF_ArduBridge import max7300_class as MAX7300     #< MAX7300 port extender 
from GSOF_ArduBridge import threadPID_HW11 as threadPID  #< Closed loop controller for temperature control
from GSOF_ArduBridge import UDP_Send                     #< Send telemetry over UDP

def extEval(s):
    s=str(s)
    print(s)
    eval(s)

def close():
    if udpConsol != False:
        udpConsol.active = False
    setup.stop()

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    from modules import Chip104_protocol as protocol #<--Your experiment protocol file name
    port = "COM10"               #< Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2          #< ArduBridge_V1.0 uses 115200 other versions use 230400 = 115200*2 
    ONLINE = True#False          #< True to enable work with real Arduino, False for simulation only
    PID1 = False                 #< True / False to build a PID controller
    PID2 = False                 #< True / False to build a PID controller
    ELEC_EN = True #False        #< True to enable the real electrodes, False for simulation only
    STACK_BUILD = [
        MAX7300.Max7300ExtGPIO(devID=0x40), #1 Top
        MAX7300.Max7300ExtGPIO(devID=0x41), #1 Bottom

        MAX7300.Max7300ExtGPIO(devID=0x42), #2 Top
        MAX7300.Max7300ExtGPIO(devID=0x43), #2 Bottom

        MAX7300.Max7300ExtGPIO(devID=0x44), #3 Top
        MAX7300.Max7300ExtGPIO(devID=0x45), #3 Bottom

        #MAX7300.Max7300ExtGPIO(devID=0x46), #4 Top
        #MAX7300.Max7300ExtGPIO(devID=0x47), #4 Bottom
        ]

    PORT_BASE = 8000 #7000                       #< Port to send status packets
    REMOTE_CTRL_PORT = None #PORT_BASE +10 #None #< Port to listen to for remote commands 
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    udpSendPid = UDP_Send.udpSend(nameID='', DesIP="127.0.0.1", DesPort=PORT_BASE +0)
    udpSendChip = UDP_Send.udpSend(nameID='', DesIP="127.0.0.1", DesPort=PORT_BASE +1)
    udpCamMgr = UDP_Send.udpSend(nameID='', DesIP="127.0.0.1", DesPort=PORT_BASE +3)
    udpConsol = False
    if REMOTE_CTRL_PORT != None:
        udpConsol = udpControl.udpControl(nameID="udpIDLE", RxPort=REMOTE_CTRL_PORT, callFunc=extEval)
        print("Remote-Consol-Active on port %s\n"%(str(REMOTE_CTRL_PORT)))
    print("Using port %s at %d"%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate, logLevel=logging.INFO )
    if ONLINE:
        ardu.OpenClosePort(1)
        print("Connecting to Arduino ON-LINE.")
    else:
        print("Arduino OFF-LINE. Simulation mode")
    
    ExtGpio = []
    if STACK_BUILD != []:
        ardu.i2c.setFreq(400000) #< MAX7300 maximum clock rate
        ExtGpio = ElectrodeGpioStack.ExtGpioStack(i2c=ardu.i2c, extGpioStack=STACK_BUILD, v=False)#True)
        ExtGpio.init()
        ExtGpio.init()
        ardu.ExtGpio = ExtGpio
        ardu.Reset()
        print("External GPIO Ready\n")
    else:
        print("External GPIO skipped\n")

    if PID1 == True:
        PID = threadPID.ArduPidThread(bridge=ardu,
                                      nameID="PID1",       # Process name
                                      Period=0.5,          # The PID calculation cycle-time
                                      fbPin=0,             # The analog pin of the temperture sensor
                                      outFunc=hw.pwmA,     # The PWM output to the H-Bridge
                                      viewer={"UDP1": udpSendPid1.Send}
                                      )
        PID.PID.Kp = 10.0
        PID.PID.Ki = 1.0
        PID.PID.Kd = 0.0
        PID.enOut = True
        hw.pwmA_init()
        print("type PID.start() to start the PID thread\n")

    if PID2 == True:
        PID2 = threadPID.ArduPidThread(bridge=ardu,
                                      nameID="PID2",
                                      Period=0.5,          # The PID calculation cycle-time
                                      fbPin=1,             # The analog pin of the temperture sensor
                                      outFunc=hw.pwmB,     # The PWM output to the H-Bridge
                                      viewer={"UDP2": udpSendPid2.Send}
                                      )
        PID2.PID.Kp = 10
        PID2.PID.Ki = 1.0
        PID2.PID.Kd = 0.0
        PID2.enOut = True
        hw.pwmB_init()
        print("type PID2.start() to start the PID2 thread\n")

    setup = protocol.Setup(ExtGpio=ExtGpio, gpio=ardu.gpio, chipViewer=udpSendChip.Send)
    setup.enOut(ELEC_EN)
