#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 07/July/2023
"""

#Basic modules to load
import time
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge.device import SSD1306_class
from TestScripts import testScripts

pin_dispON = 7 #9

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

### Helper function for encoder read/write
def dispON(on):
    ardu.gpio.pinMode(pin_dispON, 0)
    ardu.gpio.digitalWrite(pin_dispON, on&1)

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = 'COM10'       #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2  #<--Leave as is
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate, logLevel=logging.INFO )
    
    # 128x32 display with hardware I2C:
    disp = SSD1306_class.SSD1306_128_64(rst=None, i2c=ardu.i2c)
    test = testScripts.test(disp=disp)

    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')
        
    ardu.i2c.setFreq(100000)  #< Try to increase to improve speed

    test.printHelp()
    test.config()
