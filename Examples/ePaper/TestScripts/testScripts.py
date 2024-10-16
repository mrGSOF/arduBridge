#!/usr/bin/env python
"""
Script to test the motion controller, steppers, encoder and optical setup

By: Guy Soffer
Date: 01/Apr/2021
"""

import time, math
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class test():
    def __init__(self, disp):
        self.disp = disp
        #self.printHelp()
        
    def printHelp(self):
        print("Use test.config() to initialize the motion-controller for a test")
        print("Use test.snsAccuracyTest(steps=range(0,360,5), units='psi')")
        #print("Use test.snsNoiseTest()")

    def config(self):
        self.disp.begin() #< Initialize library.

    def cls(self):
        self.disp.clear() #< Clear display.
        self.disp.display()
        
    def image(self, filename='happycat_oled_64.ppm', scale=True):
        #image = Image.open(filename).convert('1')
        # Alternatively load a different format image, resize it, and convert to 1 bit color.
        image = Image.open(filename)

        if scale:
            ratioX = self.disp.width/image.width
            ratioY = self.disp.height/image.height
            sf = min([ratioX, ratioY])
            #image = image.resize( (int(image.width*sf), int(image.height*sf)), Image.ANTIALIAS )
            image = image.resize( (self.disp.width, self.disp.height), Image.ANTIALIAS )
        image = image.convert('1')

        # Display image.
        self.disp.image(image)
        self.disp.display()
        
    def animateText(self, text=False):
        if test == False:
            text = "SSD1306 ORGANIC LED DISPLAY. THIS IS AN OLD SCHOOL DEMO SCROLLER!! GREETZ TO: LADYADA & THE ADAFRUIT CREW, TRIXTER, FUTURE CREW, AND FARBRAUSCH"
        self.cls()
        
        width = self.disp.width
        height = self.disp.height

        # Create image buffer.
        # Make sure to create image with mode '1' for 1-bit color.
        image = Image.new('1', (width, height))

        # Load default font.
        font = ImageFont.load_default()

        # Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as this python script!
        # Some nice fonts to try: http://www.dafont.com/bitmap.php
        # font = ImageFont.truetype('Minecraftia.ttf', 8)

        # Create drawing object.
        draw = ImageDraw.Draw(image)

        # Define text and get total width.
        maxwidth, unused = draw.textsize(text, font=font)

        # Set animation and sine wave parameters.
        amplitude = height/4
        offset = height/2 - 4
        velocity = -2
        startpos = width

        # Animate text moving in sine wave.
        print('Press Ctrl-C to quit.')
        pos = startpos
        while True:
            # Clear image buffer by drawing a black filled box.
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            # Enumerate characters and draw them offset vertically based on a sine wave.
            x = pos
            for i, c in enumerate(text):
                # Stop drawing if off the right side of screen.
                if x > width:
                    break
                # Calculate width but skip drawing if off the left side of screen.
                if x < -10:
                    char_width, char_height = draw.textsize(c, font=font)
                    x += char_width
                    continue
                # Calculate offset from sine wave.
                y = offset +math.floor(amplitude*math.sin(x/float(width)*2.0*math.pi))
                # Draw text.
                draw.text((x, y), c, font=font, fill=255)
                # Increment x position based on chacacter width.
                char_width, char_height = draw.textsize(c, font=font)
                x += char_width
            # Draw the image buffer.
            self.disp.image(image)
            self.disp.display()
            # Move position for next frame.
            pos += velocity
            # Start over if text has scrolled completely off left side of screen.
            if pos < -maxwidth:
                pos = startpos
            # Pause briefly before drawing next frame.
            #time.sleep(0.1)

    def button(self):
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = self.disp.width
        height = self.disp.height
        image = Image.new('1', (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle( (0,0,width,height), outline=0, fill=0 )

        try:
            while 1:
                if GPIO.input(U_pin): # button is released
                    draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
                else: # button is pressed:
                    draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  #Up filled

                if GPIO.input(L_pin): # button is released
                    draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left
                else: # button is pressed:
                    draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  #left filled

                if GPIO.input(R_pin): # button is released
                    draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right
                else: # button is pressed:
                    draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1) #right filled

                if GPIO.input(D_pin): # button is released
                    draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down
                else: # button is pressed:
                    draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1) #down filled

                if GPIO.input(C_pin): # button is released
                    draw.rectangle((20, 22,40,40), outline=255, fill=0) #center 
                else: # button is pressed:
                    draw.rectangle((20, 22,40,40), outline=255, fill=1) #center filled

                if GPIO.input(A_pin): # button is released
                    draw.ellipse((70,40,90,60), outline=255, fill=0) #A button
                else: # button is pressed:
                    draw.ellipse((70,40,90,60), outline=255, fill=1) #A button filled

                if GPIO.input(B_pin): # button is released
                    draw.ellipse((100,20,120,40), outline=255, fill=0) #B button
                else: # button is pressed:
                    draw.ellipse((100,20,120,40), outline=255, fill=1) #B button filled

                # Display image.
                self.disp.image(image)
                disp.display()   

                time.sleep(0.1) 


        except KeyboardInterrupt: 
            GPIO.cleanup()

    def shape(self):
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = self.disp.width
        height = self.disp.height
        image = Image.new('1', (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = 2
        shape_width = 20
        top = padding
        bottom = height-padding
        # Move left to right keeping track of the current x position for drawing shapes.
        x = padding
        # Draw an ellipse.
        draw.ellipse((x, top , x+shape_width, bottom), outline=255, fill=0)
        x += shape_width+padding
        # Draw a rectangle.
        draw.rectangle((x, top, x+shape_width, bottom), outline=255, fill=0)
        x += shape_width+padding
        # Draw a triangle.
        draw.polygon([(x, bottom), (x+shape_width/2, top), (x+shape_width, bottom)], outline=255, fill=0)
        x += shape_width+padding
        # Draw an X.
        draw.line((x, bottom, x+shape_width, top), fill=255)
        draw.line((x, top, x+shape_width, bottom), fill=255)
        x += shape_width+padding

        # Load default font.
        font = ImageFont.load_default()

        # Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        #font = ImageFont.truetype('Minecraftia.ttf', 8)

        # Write two lines of text.
        draw.text((x, top),    'Hello',  font=font, fill=255)
        draw.text((x, top+20), 'World!', font=font, fill=255)

        # Display image.
        self.disp.image(image)
        self.disp.display()
