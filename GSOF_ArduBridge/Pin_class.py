
class Pin():
    INPUT  = 1
    OUTPUT = 0
    def __init__(self, gpio, pin):
        self.pin = pin
        self.gpio = gpio

    def high(self):
        self.gpio.setPin(self.pin, 1)
        return self

    def low(self):
        self.gpio.setPin(self.pin, 0)
        return self

    def set(self, val):
        self.gpio.setPin(self.pin, int(bool(val)))
        return self

    def get(self, val):
        return self.gpio.getPin(self.pin)

    def mode(self, mode):
        self.gpio.pinMode(self.pin, mode)
        return self
