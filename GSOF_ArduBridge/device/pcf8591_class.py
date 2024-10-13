"""
    This file is part of GSOF_ArduBridge.

    GSOF_ArduBridge is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GSOF_ArduBridge is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GSOF_ArduBridge.  If not, see <https://www.gnu.org/licenses/>.

Python class for interacting with the PCF8591 I2C 8-Bit 4 channel ADC + DAC.
It communicates with the host device via I2C and has an interrupt output that can be used to signal when the device's input pins have changed.

The class has several methods:
__init__(self, i2c, dev=0x20): The constructor for the class.
It initializes the class with an I2C object and the device address of the PCF8591 (0x48 by default).

digitalRead(self, pin, thrs): Reads the current state of a single input pin and returns it as a 0 or 1.

setPin(self, pin, val, high): Sets the state of a single output pin to either 0 or 1.

digitalWrite(self, pin, val, high): Alias for setPin. It emulates the digitalWrite function from the Arduino API.
"""

class PCF8591():
    DAC   = 0x40

    ### Single ended
    A0_VS = 0x40
    A1_VS = 0x41
    A2_VS = 0x42
    A3_VS = 0x43

    ### Reference to A3
    A0_A3 = 0x50
    A1_A3 = 0x51
    A2_A3 = 0x52

    A0_A1 = 0x70
    A2_A3 = 0x71

    ### Differencial
    DIFF_A0 = 0x70
    DIFF_A1 = 0x71

    def __init__(self, i2c, dev=0x48):
        self.i2c = i2c
        self.dev = dev
        self.adcVss  = (self.A0_VS, self.A1_VS, self.A2_VS, self.A3_VS)
        self.adcRef  = (self.A0_A3, self.A1_A3, self.A2_A3)
        self.adcDiff = (self.A0_A1, self.A2_A3)

    def analogReadDiff(self, ch) -> int:
        self.i2c.writeRaw(self.dev, [self.adcDiff[ch]])
        return self.i2c.readRaw(self.dev, 1)[0]

    def analogReadRef(self, ch) -> int:
        self.i2c.writeRaw(self.dev, [self.adcRef[ch]])
        return self.i2c.readRaw(self.dev, 1)[0]

    def analogRead(self, ch) -> int:
        self.i2c.writeRaw(self.dev, [self.adcVss[ch]])
        return self.i2c.readRaw(self.dev, 1)[0]
    
    def analogWrite(self, value) -> None:
        self.i2c.writeRaw(self.dev, [self.DAC, value&0xff])
    
    def digitalRead(self, pin, thrs=0x7f) -> int:
        """Return 0 if voltage below thrs, else returns 1"""
        return (self.analogRead(pin) > thrs)
        
    def setPin(self, val, high=0xff) -> None:
        """Sets the DAC to high if val == 1, else sets DAC to 0"""
        val = high*int(bool(val))
        self.analogWrite(val)

    def digitalWrite(self, pin, val, high=0xff) -> None:
        """
        Emulates an Arduino digitalWrite command to set a GPO pin.
        pin: The channel that should be updated with the new values (0..7)
        val: integer value 0 or 1 where 0 is OFF and 1 in ON.
        """
        self.setPin(pin, val)
