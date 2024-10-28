#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 18/Apr/2023
"""

#Basic modules to load
import logging
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge import ArduShield_Uno

def quickHelp():
    print("Quick help:")
    print("ardu.ws.setConfig(pin=13, leds=10) #< 10 LEDs OFF")
    print("ardu.ws.setConfig(pin=13, leds=10, red=10, green=10, blue=10)")
    print("ardu.ws.ledWrite([(100,0,0),(0,100,0),(0,0,100)]*3) #< 9 LEDs to R,G,B")
    
if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = "auto"          #< Change to the correct COM to access the Arduino
    #port = "/dev/ttyUSB0" #< Under Linux
    baudRate = 115200*2    #< Leave as is (230400 bits per second)
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate, logLevel=logging.INFO )
    ards = ArduShield_Uno.ArduBridge_Shield( ardu, an_ref=3.3 )

    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')
    quickHelp()

    #\/\/\/ REST OF YOUR CODE GOES HERE \/\/\/
    
    #/\/\/\        CODE BLOCK END       /\/\/\


