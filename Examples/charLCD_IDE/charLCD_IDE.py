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
from GSOF_ArduBridge.device import pcf8574_class
from GSOF_ArduBridge.device import charLCD as LCD

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

def lcdWrite(value):
    lcd_gpio.setPort(value)

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


    # Initialize the LCD using the pins above.
    lcd_columns = 8
    lcd_rows = 2
    lcd_gpio = pcf8574_class.PCF8574(ardu.i2c, dev=0x20)

    lcd = LCD.CharLCD(rs=0, rw=1, en=2, backlight=3,
                      d4=4, d5=5, d6=6, d7=7,
                      columns=lcd_columns, rows=lcd_rows,
                      pwm=None, gpio=lcdWrite)
    
    lcd.init(backlight=1)

    # Print a two line message
    lcd.print('Hello\nworld!')

    # Wait 5 seconds
    time.sleep(5.0)

    # Demo showing the cursor.
    lcd.clear()
    lcd.showCursor(True)
    lcd.print('Show\ncursor')

    time.sleep(5.0)

    # Demo showing the blinking cursor.
    lcd.clear()
    lcd.blink(True)
    lcd.print('Blink\ncursor')

    time.sleep(5.0)

    # Stop blinking and showing cursor.
    lcd.showCursor(False)
    lcd.blink(False)

    # Demo scrolling message right/left.
    lcd.clear()
    message = 'Scroll'
    lcd.print(message)
    for i in range(lcd_columns-len(message)):
        time.sleep(0.5)
        lcd.moveRight()
    for i in range(lcd_columns-len(message)):
        time.sleep(0.5)
        lcd.moveLeft()

    # Demo turning backlight off and on.
    lcd.clear()
    lcd.print('Flash\nbacklight')
    time.sleep(3.0)
    # Turn backlight off.
    lcd.setBacklight(0)
    time.sleep(2.0)
    # Change message.
    lcd.clear()
    lcd.print('Goodbye!')
    # Turn backlight on.
    lcd.setBacklight(1)

