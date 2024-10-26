import os, time, logging
from PIL import Image,ImageDraw,ImageFont


def demo(epd, test=None):
    picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
    fontFile = os.path.join(picdir, 'Font.ttc')
    print(fontFile)
    font24 = ImageFont.truetype(fontFile, 24)
    font18 = ImageFont.truetype(fontFile, 18)
    font35 = ImageFont.truetype(fontFile, 35)

    logging.basicConfig(level=logging.DEBUG)
    logging.info("epd2in7 Demo")
    try:
    
        logging.info("init and Clear")
        epd.initBwr()
        epd.clear()
        
        if (1 in test) or (test==None):
            # Drawing on the Horizontal image
            logging.info("1.Drawing on the Horizontal image...")
            Himage = Image.new('1', epd.getResolution(), 255)  #< clear the frame with 255
            draw = ImageDraw.Draw(Himage)
            draw.text((10, 0), 'hello world', font = font24, fill = 0)
            draw.text((10, 20), '2.7inch e-Paper', font = font24, fill = 0)

            draw.line((20, 50, 70, 100), fill = 0)
            draw.line((70, 50, 20, 100), fill = 0)
            draw.rectangle((20, 50, 70, 100), outline = 0)

            draw.line((165, 50, 165, 100), fill = 0)
            draw.line((140, 75, 190, 75), fill = 0)
            draw.arc((140, 50, 190, 100), 0, 360, fill = 0)

            draw.rectangle((80, 50, 130, 100), fill = 0)
            draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
            epd.displayBwr(epd.getBufferBwr(Himage))

            time.sleep(1) #< -------------

        if (2 in test) or (test==None):
            logging.info("Partial refresh")
            image = Image.new('1', epd.getResolution(), 0)  #< clear the frame with 0
            draw = ImageDraw.Draw(image)

            color = 1
            x = 16
            y = 16
            dx = epd.width
            dy = 48
            draw.rectangle((x, y, x+dx, y+dy), fill = color^1)
            draw.text((x, y), "Partial Refresh" , font = font35, fill = color)
            epd.displayPartial(x, y, x+dy, y+dy, epd.getbuffer(image))

            y = 0
            r = 24
            d = 2*r
            dx = 8*int((2*(r+1) +8)/8)
            dy = dx
            color = 1
            for iY in range(0, int(epd.height/dy) ):
                x = 0
                for iX in range(0, int(epd.width/dx) ):
                    draw.rectangle((x, y, y+dy, y+dy), fill = color^1)
                    draw.chord((x, y, x+d, y+d), 0, 360, fill = color)
                    draw.text((x+5, y+10), "%dx%d"%(iX,iY) , font = font18, fill = color^1)
                    epd.displayPartial(x, y, x+dy, y+dy, epd.getbuffer(image))
                    x += dx
                y += dy

            time.sleep(1) #< -------------

        if (3 in test) or (test==None):
            logging.info("Gray scale circuils")
            epd.init4Gray()
            image = Image.new('L', epd.getResolution(), epd.GRAY1)  #< clear the frame with 0
            draw = ImageDraw.Draw(image)

            logging.info("Read bmp file on window")
            bmp = Image.open(os.path.join(picdir, 'demo.jpg'))
            image.paste(bmp, (0, 20))

            x = 50
            y = 10
            r = 20
            d = 2*r
            dx = d +10
            colors = (epd.GRAY2, epd.GRAY3, epd.GRAY4)
            x = int((epd.width -dx*len(colors))/2)
            for color in colors:
                draw.chord((x, y, x+d, y+d), 0, 360, fill = color)
                x += dx

            logging.info("Read bmp file on window")
            bmp = Image.open(os.path.join(picdir, 'GSOF.bmp'))
            image.paste(bmp, (0, 0))

            epd.display4Gray(epd.getBuffer4Gray(image))

            time.sleep(1) #< -------------
     
        if (4 in test) or (test==None):
            epd.clear()
            image = Image.new('1', epd.getResolution(), 0)  # 255: clear the frame
            draw = ImageDraw.Draw(image)
            print("Support for partial refresh, but the refresh effect isn't good and it's not recommended")
            for j in range(0, int(20)):
                draw.rectangle((8, 80, 44, 155), fill = 0)
                draw.text((8, 80), str(j) , font = font35, fill = 1)
                draw.text((8, 120), str(20-j) , font = font35, fill = 1)
                epd.displayPartial(8, 80, 44, 155, epd.getbuffer(image))
                print(j)
                time.sleep(0.2);

        logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        exit()

