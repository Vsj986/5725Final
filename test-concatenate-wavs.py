import RPi.GPIO as GPIO
import os
import pygame
import time
import busio
from board import SCL, SDA
from adafruit_trellis import Trellis
from pygame.locals import *   # for event MOUSE variables
import setting
from pydub import AudioSegment
from pydub.playback import play

# Create the I2C interface
i2c = busio.I2C(SCL, SDA)

# Create a Trellis object
trellis = Trellis(i2c)  # 0x70 when no I2C address is supplied

# instrument files
wavefiles = ['01.wav','02.wav','03.wav','04.wav','05.wav','06.wav','07.wav','08.wav',
  '09.wav','10.wav','11.wav','12.wav','13.wav','14.wav','15.wav','16.wav']

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def GPIO27_callback(channel):
    exit(0)
    print(27)
    
def GPIO19_callback(channel):
    print("callback 19")
    #cmd1 = 'arecord -D hw:1,0 -d 5 -f S24_3LE /home/pi/Final/loop1.wav -c2 -r48000 &'
    #os.system(cmd1)
    concatenate_wav("/home/pi/Final/loop1.wav", wavefiles)
    loop1 = AudioSegment.from_wav("output.wav")
    play(mixed)


def GPIO26_callback(channel):
    print("callback 26")
    cmd2 = 'arecord -D hw:1,0 -d 5 -f S24_3LE /home/pi/Final/loop2.wav -c2 -r48000 &'
    os.system(cmd2)

GPIO.add_event_detect(27,GPIO.FALLING, callback=GPIO27_callback)
GPIO.add_event_detect(19,GPIO.FALLING, callback=GPIO19_callback)
GPIO.add_event_detect(26,GPIO.FALLING, callback=GPIO26_callback)


def concatenate_wav(orders, wavs):                                                  
    combined_wav = AudioSegment.empty()
	for order, wav in zip(orders, wavs):                                                            
    	order = AudioSegment.from_wav(wav)                                                          
    	combined_wav += order      
        combined_wav.export(os.path.join(os.path.dirname(__file__), "output.wav"), format="wav")






