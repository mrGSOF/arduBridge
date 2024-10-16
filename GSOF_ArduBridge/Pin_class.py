
class Pin():
    INPUT  = 1
    OUTPUT = 0
    def __init__(self, gpio, pin, invpolarity=0):
        self.pin = pin
        self.gpio = gpio
        self.invpolarity = int(bool(invpolarity))

    def high(self):
        self.gpio.setPin(self.pin, 1^self.invpolarity)
        return self

    def low(self):
        self.gpio.setPin(self.pin, 0^self.invpolarity)
        return self

    def set(self, val):
        self.gpio.setPin(self.pin, int(bool(val))^self.invpolarity)
        return self

    def get(self):
        return self.gpio.getPin(self.pin)^self.invpolarity

    def mode(self, mode, invpolarity=None):
        self.gpio.pinMode(self.pin, mode)
        if invpolarity != None:
            self.invpolarity = int(bool(invpolarity))
        return self
