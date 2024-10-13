#!/usr/bin/env python
"""
Script to build an GSOF_ArduBridge environment over the GSOF_ArduBridgeSielf
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 15/Oct/2024
"""

#Basic modules to load
import time, logging
from GSOF_ArduBridge import ArduBridge     #< The GSOF_arduBridge classes
from GSOF_ArduBridge import ArduShield_Uno #< The GSOF_arduBridgeShield library
from GSOF_ArduBridge.device import pca9685_class
from GSOF_ArduBridge.device import Servo

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

def test(ch, N=2, acc=0.0008, dt=0.05):
    srv = Servo.Servo(setServo=pwm.setPulseWidth, ch=ch, minPosition=0.001, maxPosition=0.002)
    for i in range(0,N):
        srv.servoScurve(p0=0.0015, p1=0.0020, acc=acc, dt=dt)
        srv.servoScurve(p0=0.0020, p1=0.0015, acc=acc, dt=dt)
        srv.servoScurve(p0=0.0015, p1=0.0010, acc=acc, dt=dt)
        srv.servoScurve(p0=0.0010, p1=0.0015, acc=acc, dt=dt)

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

    pwm = pca9685_class.PCA9685(i2c=ardu.i2c, dev=0x40)
    pwm.init(v=False).setPwmFrequency(50, v=True)
    servo = Servo.Servo(setServo=pwm.setPulseWidth, ch=4, minPosition=0.001, maxPosition=0.002)
    
    
    print("servo = Servo.Servo(setServo=pwm.setPulseWidth, ch=4, minPosition=0.001, maxPosition=0.002)")
    print("servo.servoMode(1) #< Servo on PWM connector#")
    print("servo.servoSet(pos)  #< Step transition to target position (0 to 250)")
    print("servo.servoScurve(p0=0.001, p1=0.002, acc=0.0008, dt=0.05) #< Smooth transition from -> to positions")
