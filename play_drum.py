import pygame
import time
from board import SCL, SDA
import busio
import os
#from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_trellis import Trellis


#create the i2c object for the trellis
i2c = busio.I2C(SCL, SDA)
 
#create the trellis
trellis = Trellis(i2c)

trellis.led.fill(True)

OFF = (0, 0, 0)
CYAN = (0, 255, 255)

#create a list of wav file names
wavfiles = ['01.wav','02.wav','03.wav','04.wav','05.wav','06.wav','07.wav','08.wav',
'09.wav','10.wav','11.wav','12.wav','13.wav','14.wav','15.wav','16.wav']
 
def blink(event):
    #turn the LED on when a rising edge is detected
    if event.edge == NeoTrellis.EDGE_RISING:
        trellis.pixels[event.number] = CYAN
        #access event.number--number in the list
        #create the path to the audio file
        os.system('omxplayer /home/pi/Final/drums/'+wavfiles[event.number]+'&') # check whether to use '&'
    #turn the LED off when a rising edge is detected
    elif event.edge == NeoTrellis.EDGE_FALLING:
        trellis.pixels[event.number] = OFF
        
for i in range(16):
    #activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    #activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    #set all keys to trigger the blink callback
    trellis.callbacks[i] = blink

while True:
    #call the sync function call any triggered callbacks
    trellis.sync()
    #the trellis can only be read every 10 millisecons or so
    time.sleep(.02)
    
    
