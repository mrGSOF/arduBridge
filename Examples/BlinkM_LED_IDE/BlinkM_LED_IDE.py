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
from GSOF_ArduBridge.device import blinkM_class

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

def test(N=10):
    led.stop()
    led.off()
    for f in range(0, N):
        color = [0,0,0]
        for comp in range(0,3):
            for v in range(0,256,5):
                color[comp] = v
                led.setRgb(red=color[0], green=color[1], blue=color[2])
                print(str(color))
                time.sleep(0.1)
    led.off()

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

    led = blinkM_class.BlinkM(i2c=ardu.i2c, dev=0x0) #< Broadcase to any device (default 0x9)

    print("led.getVersion()")
    print("led.stop()")
    print("led.play()")
    print("led.off()")
    print("led.setRgb(red=50, green=0, blue=0)")
    print("led.getRgb()")
    print("led.fadeToRgb(red=0x40, green=0x40, blue=0x40)")
    print("led.brightness(3) #< 0 to 7")
    print("test(N=1)")
