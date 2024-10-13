#!/usr/bin/env python
"""
Script to build an GSOF_ArduBridge environment over the GSOF_ArduBridgeSielf
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 08/Mar/2021
"""

#Basic modules to load
import time, logging
from GSOF_ArduBridge import ArduBridge     #< The GSOF_arduBridge classes
from GSOF_ArduBridge import ArduShield_Uno #< The GSOF_arduBridgeShield library

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

def test(pwmCh, N=2, acc=800, dt=0.05):
    ards.servoMode(pwmCh, 1)
    for i in range(0,N):
        ards.servoScurve(pwmCh, p0=95, p1=250, acc=acc, dt=dt)
        ards.servoScurve(pwmCh, p0=250, p1=95, acc=acc, dt=dt)
        ards.servoScurve(pwmCh, p0=95, p1=0, acc=acc, dt=dt)
        ards.servoScurve(pwmCh, p0=0, p1=95, acc=acc, dt=dt)

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = 'auto'        #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2  #<--Leave as is
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate, logLevel=logging.INFO ) #< The GSOF_arduBridge core object
    ards = ArduShield_Uno.ArduBridge_Shield(ardu)                                   #< The GSOF_arduBridge HW shield object
    
    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')
        
    ### Configure the pins for servo control
    ards.servoMode(2, ardu.gpio.SERVO) #< Servo on PWM connector#2
    ards.servoMode(3,ardu.gpio.SERVO) #< Servo on PWM connector#3

    ### Set the servo position 
    ards.servoSet(2,50)               #< Step transition to target position (0 to 250)
    ards.servoSet(3,170)
    time.sleep(1.0)
    ards.servoScurve(2, 50, 170, 800) #< Smooth transition from -> to positions 
    ards.servoScurve(3, 170, 50, 500)

    print("ards.servoMode(pwmCh, 1) #< Servo on PWM connector#")
    print("ards.servoSet(pwmCh, pos)  #< Step transition to target position (0 to 250)")
    print("ards.servoScurve(pwmCh, p0=0, p1=250, acc=800, dt=0.05) #< Smooth transition from -> to positions")
    print("test(pwmCh, N=2, acc=800, dt=0.05)")

