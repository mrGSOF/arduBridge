#!/usr/bin/env python
"""
Script to build an GSOF_ArduBridge environment over the GSOF_ArduBridgeSielf
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 19/Feb/2024
"""

#Basic modules to load
import time
from GSOF_ArduBridge import ArduBridge     #< The GSOF_arduBridge classes
from GSOF_ArduBridge import ArduShield_Uno #< The GSOF_arduBridgeShield library

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

def JoystickTest(ardu):
    for i in range(0,100):
            x = ardu.an.analogRead(4) -406
            y = ardu.an.analogRead(5) -406
            print("%d, %d"%(x,y))
            time.sleep(0.05)

def CameraMovement(ards):
    ardu = ards.ardu
    ards.servoMode(1,1)
    ards.servoMode(2,1)
    x,y = (80,80)
    while (y > 40) and (y < 160):
            dx = (ardu.an.analogRead(5)-652)/20
            dy = (ardu.an.analogRead(4)-632)/20
            if abs(dx) > 1:
                x += dx
                if x > 165:
                    x = 165
                elif x < 35:
                    x = 35
                
            if abs(dy) > 1:
                y += dy
                if y < 40:
                    y = 40
                elif y > 180:
                    y = 180

            ards.servoSet(1,x)
            ards.servoSet(2,y)
            time.sleep(0.1)

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = 'COM6'        #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2  #<--Leave as is
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate, logLevel=logging.INFO ) #< The GSOF_arduBridge core object
    ards = ArduBridge_HW.ArduBridge_Shield(ardu)                                   #< The GSOF_arduBridge HW shield object
    
    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')
        
    ### Configure the pins for servo control
    ards.servoMode(2,1) #< Servo on PWM connector#1
    ards.servoMode(3,1) #< Servo on PWM connector#2

    while True:
        CameraMovement(ards)
        #JoystickTest(ardu)  
