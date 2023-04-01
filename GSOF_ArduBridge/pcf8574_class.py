"""
PCF8574 8-Bit I2C I/O Expander with Interrupt
"""

"""
This is a Python class for interacting with the PCF8574 I2C I/O expander. The PCF8574 is a 8-bit input/output (I/O) expander that can be used to add additional I/O capabilities to a microcontroller or microprocessor. It communicates with the host device via I2C and has an interrupt output that can be used to signal when the device's input pins have changed.

The class has several methods:

__init__(self, i2c, dev=0x20): This is the constructor for the class. It initializes the class with an I2C object and the device address of the PCF8574 (which is a constant set to 0x20).

_checkPin(self, pin): This is a helper method that checks if a pin number is valid (i.e., within the range 0 to 7). If the pin number is invalid, it raises a ValueError.

getPort(self): This method reads the current state of all of the device's input pins and returns it as a single byte.

setPort(self, val): This method sets the state of all of the device's output pins based on a single byte. The least significant bit of the byte corresponds to the first output pin and the most significant bit corresponds to the last output pin.

getPin(self, pin): This method reads the current state of a single input pin and returns it as a 0 or 1.

digitalRead(self, pin): This method is an alias for getPin.

setPin(self, pin, val): This method sets the state of a single output pin to either 0 or 1.

digitalWrite(self, pin, val): This method is an alias for setPin. It emulates the digitalWrite function from the Arduino API.

pinPulse(self, pin, onTime): This method pulses an output pin by setting it to 1 for a specified amount of time and then setting it back to 0.

togglePin(self, pin): This method toggles the state of a single output pin. If the pin is currently 0, it sets it to 1, and if it is currently 1, it sets it to 0.
"""

class PCF8574():
    def __init__(self, i2c, dev=0x20):
        self.i2c = i2c
        self.dev = dev

    def _checkPin(self, pin):
        if not 0 <= pin <= 7: #< # pin valid range 0..7
            raise ValueError( "Invalid pin# %d (Use 0-7)"%(pin) )
        return pin

    def getPort(self):
        ##self._i2c.read(self._address, self._port)
        val = self.i2c.readRaw(self.dev, 1)
        return val

    def setPort(self, val):
        self.i2c.writeRaw(self.dev, [val&0xff])

    def getPin(self, pin):
        pin = self._checkPin(pin)
        post = self.getPort()
        if (port&(1<<pin)) != 0:
            return  1
        return 0

    def digitalRead(self, pin):
        return self.getPin(pin)
        
    def setPin(self, pin, val):
        pin = self._checkPin(pin)
        pin_mask = (1<<pin)
        port = self._read()
        if port&pin_mask != val:
            port &= (~pin_mask)
            port |= ((val&1)<<pin)
            self.setPort(port)

    def digitalWrite(self, pin, val):
        """
        Emulates an Arduino digitalWrite command to set a GPO pin.
        pin: The channel that should be updated with the new values (0..15)
        val: integer value 0 or 1 where 0 is OFF and 1 in ON.
        """
        self.setPin(pin, val)
        return 1

    def pinPulse(self, pin, onTime):
        """
        Pulse the the specific pin# on the arduino GPO
        """
        self.digitalWrite(pin, 1)
        time.sleep(onTime)
        self.digitalWrite(pin, 0)
        return 1

    def togglePin(self, pin):
        pin = self.validate_pin(pin)
        self._port[0] ^= (1 << (pin))
        self._write()
