# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time

# Commands
LCD_CLEARDISPLAY        = 0x01
LCD_RETURNHOME          = 0x02
LCD_ENTRYMODESET        = 0x04
LCD_DISPLAYCONTROL      = 0x08
LCD_CURSORSHIFT         = 0x10
LCD_FUNCTIONSET         = 0x20
LCD_SETCGRAMADDR        = 0x40
LCD_SETDDRAMADDR        = 0x80

# Entry flags
LCD_ENTRYRIGHT          = 0x00
LCD_ENTRYLEFT           = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Control flags
LCD_DISPLAYON           = 0x04
LCD_DISPLAYOFF          = 0x00
LCD_CURSORON            = 0x02
LCD_CURSOROFF           = 0x00
LCD_BLINKON             = 0x01
LCD_BLINKOFF            = 0x00

# Move flags
LCD_DISPLAYMOVE         = 0x08
LCD_CURSORMOVE          = 0x00
LCD_MOVERIGHT           = 0x04
LCD_MOVELEFT            = 0x00

# Function set flags
LCD_8BITMODE            = 0x10
LCD_4BITMODE            = 0x00
LCD_2LINE               = 0x08
LCD_1LINE               = 0x00
LCD_5x10DOTS            = 0x04
LCD_5x8DOTS             = 0x00

# Offset for up to 4 rows.
LCD_ROW_OFFSETS         = (0x00, 0x40, 0x14, 0x54)

# Char LCD plate GPIO numbers.
LCD_PLATE_RS            = 15
LCD_PLATE_RW            = 14
LCD_PLATE_EN            = 13
LCD_PLATE_D4            = 12
LCD_PLATE_D5            = 11
LCD_PLATE_D6            = 10
LCD_PLATE_D7            = 9
LCD_PLATE_RED           = 6
LCD_PLATE_GREEN         = 7
LCD_PLATE_BLUE          = 8

# Char LCD plate button names.
SELECT                  = 0
RIGHT                   = 1
DOWN                    = 2
UP                      = 3
LEFT                    = 4

class CharLCD():
    """Class to represent and interact with an HD44780 character LCD display."""

    def __init__(self, gpio,
                 rs=0, rw=1, en=2, backlight=3,d4=4, d5=5, d6=6, d7=7,
                 columns=16, rows=2,
                 invert_polarity=True,
                 pwm=None
                 ):
        """Initialize the LCD.  RS, EN, and D4...D7 parameters should be the pins
        connected to the LCD RS, clock enable, and data line 4 through 7 connections.
        The LCD will be used in its 4-bit mode so these 6 lines are the only ones
        required to use the LCD.  You must also pass in the number of columns and
        lines on the LCD.  

        If you would like to control the backlight, pass in the pin connected to
        the backlight with the backlight parameter.  The invert_polarity boolean
        controls if the backlight is one with a LOW signal or HIGH signal.  The 
        default invert_polarity value is True, i.e. the backlight is on with a
        LOW signal.  

        You can enable PWM of the backlight pin to have finer control on the 
        brightness.  To enable PWM make sure your hardware supports PWM on the 
        provided backlight pin and set enable_pwm to True (the default is False).
        The appropriate PWM library will be used depending on the platform, but
        you can provide an explicit one with the pwm parameter.

        The initial state of the backlight is ON, but you can set it to an 
        explicit initial state with the initial_backlight parameter (0 is off,
        1 is on/full bright).

        You can optionally pass in an explicit GPIO class,
        for example if you want to use an MCP230xx GPIO extender.  If you don't
        pass in an GPIO instance, the default GPIO for the running platform will
        be used.
        """
        # Save column and line state.
        self._cols = columns
        self._rows = rows
        
        # Save GPIO state and pin numbers.
        self._gpio = gpio
        self._rs = rs
        self._rw = rw
        self._en = en
        self._backlight = backlight
        self._d4 = d4
        self._d5 = d5
        self._d6 = d6
        self._d7 = d7
        
        # Save backlight state.
        self._pwm = pwm
        self._blpol = not invert_polarity
        self._bl_state = 0

    def init(self, backlight=None):
        # Setup backlight.
        if backlight is not None:
            self.setBacklight(int(backlight))
            
        # Initialize the display.
        self._write8(0x33)
        self._write8(0x32)
        
        # Initialize display control, function, and mode registers.
        self.displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.displayfunction = LCD_4BITMODE | LCD_1LINE | LCD_2LINE | LCD_5x8DOTS
        if self._rows > 1:
            self.displayfunction |= LCD_2LINE
            
        self.displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        
        # Write registers.
        self._write8(LCD_DISPLAYCONTROL | self.displaycontrol)
        self._write8(LCD_FUNCTIONSET | self.displayfunction)
        self._write8(LCD_ENTRYMODESET | self.displaymode)  # set the entry mode
        self.clear()
        
    def home(self):
        """Move the cursor back to its home (first line and first column)."""
        self._write8(LCD_RETURNHOME)  # set cursor position to zero
        time.sleep(0.01)  # this command takes a long time!

    def clear(self):
        """Clear the LCD."""
        self._write8(LCD_CLEARDISPLAY)  # command to clear display
        time.sleep(0.01)  # this command takes a long time!

    def setCursor(self, col, row):
        """Move the cursor to an explicit column and row position."""
        # Clamp row to the last row of the display.
        if row > self._rows:
            row = self._rows -1
        # Set location.
        self._write8(LCD_SETDDRAMADDR | (col +LCD_ROW_OFFSETS[row]))
        return self

    def enableDisplay(self, enable):
        """Enable or disable the display.  Set enable to True to enable."""
        if enable:
            self.displaycontrol |= LCD_DISPLAYON
        else:
            self.displaycontrol &= ~LCD_DISPLAYON
        self._write8(LCD_DISPLAYCONTROL | self.displaycontrol)
        return self

    def showCursor(self, show):
        """Show or hide the cursor.  Cursor is shown if show is True."""
        if show:
            self.displaycontrol |= LCD_CURSORON
        else:
            self.displaycontrol &= ~LCD_CURSORON
        self._write8(LCD_DISPLAYCONTROL | self.displaycontrol)
        return self

    def blink(self, blink):
        """Turn on or off cursor blinking.  Set blink to True to enable blinking."""
        if blink:
            self.displaycontrol |= LCD_BLINKON
        else:
            self.displaycontrol &= ~LCD_BLINKON
        self._write8(LCD_DISPLAYCONTROL | self.displaycontrol)
        return self

    def moveLeft(self):
        """Move display left one position."""
        self._write8(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    def moveRight(self):
        """Move display right one position."""
        self._write8(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)
        return self

    def setLeftToRight(self):
        """Set text direction left to right."""
        self.displaymode |= LCD_ENTRYLEFT
        self._write8(LCD_ENTRYMODESET | self.displaymode)
        return self

    def setRightToLeft(self):
        """Set text direction right to left."""
        self.displaymode &= ~LCD_ENTRYLEFT
        self._write8(LCD_ENTRYMODESET | self.displaymode)
        return self

    def autoscroll(self, autoscroll):
        """Autoscroll will 'right justify' text from the cursor if set True,
        otherwise it will 'left justify' the text.
        """
        if autoscroll:
            self.displaymode |= LCD_ENTRYSHIFTINCREMENT
        else:
            self.displaymode &= ~LCD_ENTRYSHIFTINCREMENT
        self._write8(LCD_ENTRYMODESET | self.displaymode)
        return self

    def print(self, text):
        """Write text to display.  Note that text can include newlines."""
        line = 0
        # Iterate through each character.
        for char in text:
            # Advance to next line if character is a new line.
            if char == '\n':
                line += 1
                # Move to left or right side depending on text direction.
                col = 0 if self.displaymode & LCD_ENTRYLEFT > 0 else self._cols-1
                self.setCursor(col, line)
            else:
                self._write8(ord(char), True) #< Write the character to the display.

        return self

    def setBacklight(self, backlight):
        """Enable or disable the backlight.  If PWM is not enabled (default), a
        non-zero backlight value will turn on the backlight and a zero value will
        turn it off.  If PWM is enabled, backlight can be any value from 0.0 to
        1.0, with 1.0 being full intensity backlight.
        """
        self._bl_state = 0
        if self._backlight is not None:
            if self._pwm != None:
                self._pwm.set_duty_cycle(self._backlight, self._pwm_duty_cycle(backlight))
            else:
                self._bl_state = int((bool(backlight)^bool(self._blpol)))<<self._backlight
                self._gpio(self._bl_state)
        return self

    def createChar(self, location, pattern):
        """Fill one of the first 8 CGRAM locations with custom characters.
        The location parameter should be between 0 and 7 and pattern should
        provide an array of 8 bytes containing the pattern. E.g. you can easyly
        design your custom character at http://www.quinapalus.com/hd44780udg.html
        To show your custom character use eg. lcd.message('\x01')
        """
        # only position 0..7 are allowed
        location &= 0x7
        self._write8(LCD_SETCGRAMADDR | (location << 3))
        for i in range(8):
            self._write8(pattern[i], char_mode=True)

    def _delay_us(self, microseconds):
        # Busy wait in loop because delays are generally very short (few microseconds).
        end = time.time() + (microseconds/1000000.0)
        while time.time() < end:
            pass

    def _pulseEnable(self, port):
        # Pulse the clock enable line off, on, off to send command.
        self._gpio(port)
        self._delay_us(1)       # 1 microsecond pause - enable pulse must be > 450ns
        self._gpio(1<<self._en |port)
        self._delay_us(1)       # 1 microsecond pause - enable pulse must be > 450ns
        self._gpio(port)
        self._delay_us(1)       # commands need > 37us to settle

    def _pwm_duty_cycle(self, intensity):
        # Convert intensity value of 0.0 to 1.0 to a duty cycle of 0.0 to 100.0
        intensity = 100.0*intensity
        # Invert polarity if required.
        if not self._blpol:
            intensity = 100.0-intensity
        return intensity

    def _write8(self, value, char_mode=False):
        """Write 8-bit value in character or data mode.  Value should be an int
        value from 0-255, and char_mode is True if character data or False if
        non-character data (default).
        """
        # One millisecond delay to prevent writing too quickly.
        self._delay_us(1000)
        # Set character / data bit.
        rs = int(char_mode)<<self._rs

        # Write upper 4 bits.
        port = rs | self._bl_state
        for portBit, dataBit in zip( (self._d4,self._d5,self._d6,self._d7) ,range(4,8) ):
            port |= ((value>>dataBit)&1)<<portBit
        self._pulseEnable(port)

        # Write lower 4 bits.
        port = rs | self._bl_state
        for portBit, dataBit in zip( (self._d4,self._d5,self._d6,self._d7) ,range(0,4) ):
            port |= ((value>>dataBit)&1)<<portBit
        self._pulseEnable(port)

##class CharLCD_16x1(CharLCD):
##    """Class to represent and interact with an HD44780 character LCD display."""
##
##    def __init__(self, gpio,
##                 rs=0, rw=1, en=2, backlight=3,d4=4, d5=5, d6=6, d7=7,
##                 invert_polarity=True,
##                 pwm=None
##                 ):
##        super().__init__(gpio=gpio,
##                 rs=rs, rw=rw, en=en, backlight=backlight,d4=d4, d5=d5, d6=d6, d7=d7,
##                 invert_polarity=invert_polarity,
##                 columns=16, rows=1,
##                 pwm=pwm
##                 )
##
##    def printAt(self, text):
##
##    def print(self, text):
##        """Write text to display.  Note that text can include newlines."""
##        line = 0
##        # Iterate through each character.
##        for char in text:
##            # Advance to next line if character is a new line.
##            if char == '\n':
##                line += 1
##                # Move to left or right side depending on text direction.
##                col = 0 if self.displaymode & LCD_ENTRYLEFT > 0 else self._cols-1
##                self.setCursor(col, line)
##            else:
##                self._write8(ord(char), True) #< Write the character to the display.
##
##        return self
