# Introduction
The ArduBridge (GSOF_ArduBridge) is a Python software package designed to bridge between a host computer (e.g: PC or RPI) and an Arduino.
The ArduShield (GSOF_ArduShield) is an expansion board for the Arduino Uno R3 that adds additional features and connectors to attach devices such as servos, DC motors, analog sensors, high-power actuators, etc.
The main computer runs the Python script and the ArduBridge sends the commands to the Arduino over USB(RS232). This provides a convinient way to develop real-time algorithms on the main computer and use of the sensors and actuators via the Arduino. In addition, the electronic hardware can be used without the ArduBridge software by programming the Arduino directly in C/C++.

# Shield hardware
The ArduShield includes a dual H-bridge capable of driving DC motors, Thermo Electric Coolers (TEC), and other high-power devices up to 12V / 2A.
In addition, the onboard 5V regulator eliminates the need to supply a precise voltage to drive the external peripherals and to prevent overloading the USB host.
    The ArduShield also includes connectors for easy connection of servos, analog sensors, General Input Output ports (GPIO), and devices over the Serial-Peripheral-Interface (SPI) or Inter-Integrated-Circuit I2C bus.
    Although the ArduShield can be used in various projects, it was initially designed to encapsulate the electronic circuits used in Digital-Microfluidics (DMF) setup. A unique feature of the shield is the capability to stack up additional extension boards (e.g., the Digital-Microfluidics (DMF) electrode driver) without the need for extra cables and workbench space. Another unique capability is its ability to measure the impedance between any DMF electrode and the Indium-Tin-Oxide (ITO) plate. This is extremely useful for detecting faults in droplets and estimating droplet size.
![Alt text](https://github.com/mrGSOF/arduBridge/blob/main/Documentation/basicHardwareSetup.png "Basic Hardwrae Setup")

# Installation and hardware setup
The ArduBridge Python model is a pip package installation and the firmware that runs on the Arduino is installed by programming the Arduino (also know as uploading).<br />  
## To install from PyPI use:<br />  
`pip install GSOF_ArduBridge`

## To install from cloned repository use:<br />  
`pip install .`

## Firmware upload to Arduino
1. Download the latest version of the Firmware and XLoader from the [Releases Tab](https://github.com/mrGSOF/arduBridge/releases)<br />
2. Extract the files from XLoader.zip<br />
3. Open the XLoader application.
4. Select the COM port that the Arduino is connected to.
5. Select the Hex file "Bridge_Ctrl_V21.hex" (or the most updated FW you have).
6. Press the "Upload" button and wait for the programming operation to finish after a few seconds.
![Alt text](https://github.com/mrGSOF/arduBridge/blob/main/Documentation/arduBridge_FW_upload.png "Firmware update")

## Python modules installation
Before installing the ArduShield module, make sure Python 3.7 or above is installed (https://www.python.org/)
 together with the latest pyserial module (use the command "pip install pyserial" to install it).<br />
or in short:

- Clone with `git clone https://github.com/mrGSOF/arduBridge.git`
- Install requirements `pip install -r requirements.txt`
 
Installation of the ArduBridge can be done in two ways:
1.	By double clicking the setup.bat batch file.
2.	By running the setup.py script in a command prompt ("CMD") window.

# Documentation and example code

## Basic example code for using the arduino without a shield
```python
from GSOF_ArduBridge import ArduBridge

def quickHelp():
    print("Quick help:")
    print("ardu.gpio.pinMode(pin=1, mode=ardu.gpio.INPUT)")
    print("ardu.gpio.pinMode(pin=2, mode=ardu.gpio.OUTPUT)")
    print("ardu.gpio.digitalRead(1)")
    print("ardu.gpio.digitalWrite(pin=2, val=1)")
    print("ardu.gpio.pinPulse(pin=2, onTime=2)")
    print("ardu.analogWrite(pin=3, val=128)")
    print("ardu.analogRead(pin=1)")

port = "auto"          #< Change to the correct COM to access the Arduino
#port = "/dev/ttyUSB0" #< Under Linux
baudRate = 115200*2    #< Leave as is (230400 bits per second)

print('Using port %s at %d'%(port, baudRate))
ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate)

print('Discovering ArduBridge on port %s'%(port))
if ardu.OpenClosePort(1):
    print('ArduBridge is ON-LINE.')
else:
    print('ArduBridge is not responding.')
quickHelp()
```

## Basic example code for using the arduino USING a shield
```python
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge import ArduShield_Uno

def quickHelp():
    print("Quick help:")
    print("ardu.gpio.pinMode(pin=1, mode=ardu.gpio.INPUT)")
    print("ardu.gpio.pinMode(pin=2, mode=ardu.gpio.OUTPUT)")
    print("ardu.gpio.digitalRead(1)")
    print("ardu.gpio.digitalWrite(pin=2, val=1)")
    print("ardu.gpio.pinPulse(pin=2, onTime=2)")
    print("ardu.analogWrite(pin=3, val=128)")
    print("ardu.analogRead(pin=1)")

port = "auto"          #< Change to the correct COM to access the Arduino
#port = "/dev/ttyUSB0" #< Under Linux
baudRate = 115200*2    #< Leave as is (230400 bits per second)

print('Using port %s at %d'%(port, baudRate))
ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate)
ards = ArduShield_Uno.ArduBridge_Shield( ardu, an_ref=3.3 )

print('Discovering ArduBridge on port %s'%(port))
if ardu.OpenClosePort(1):
    print('ArduBridge is ON-LINE.')
else:
    print('ArduBridge is not responding.')
quickHelp()

A detailed [user manual](https://github.com/mrGSOF/arduBridge/blob/main/Documentation/GSOF_ArduBridgeShield_UM.pdf) can be found under the Documentation folder.
[Code example](https://github.com/mrGSOF/arduBridge/tree/main/Examples) are present under the Example folder.
![Alt text](https://github.com/mrGSOF/arduBridge/blob/main/Documentation/codeTemplate.png "Basic Code Template")

Update the COM port in ArduBridge_IDE.py and run in interactive mode ("python -i ArduBridge_IDE.py")
You can interact the Arduino using the ardu and ards objects (refer to the [tutorial](https://github.com/mrGSOF/arduBridge/blob/main/Documentation/GSOF_ArduBridgeShield_UM.pdf) for further information).
 
# Acknowledgements
I want to thank the following beta testers for their valuable contributions in the developent of the ArduBridge program:
James Perry (Ph.D.), Laura Leclerc, Kenza Samlali (Ph.D.), Tzur Soffer, and Sam Little.
Their feedback and suggestions were instrumental in identifying and resolving any issues in the program. I would especially like to acknowledge James and Tzur. James used the Ardubridge in all of his academic publications and teaching new students how to use it as well. Tzur automated his room and build autonomous robots using the ArduBridge environment.
