# Basic example of turning on LEDs and handling Keypad
# button activity.

# This example uses only one Trellis board, so all loops assume
# a maximum of 16 LEDs (0-15). For use with multiple Trellis boards,
# see the documentation.
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

inst = setting.index   # instrument index
paths = ['/piano/','/violin/','/piano/','/flute/','/drum/']

# blink on key pad
# Turn on every LED, one at a time
print("Turning on each LED, one at a time...")
for i in range(16):
    trellis.led[i] = True
    time.sleep(0.1)
time.sleep(1)

# Turn off every LED
print("Turning all LEDs off...")
trellis.led.fill(False)
time.sleep(2)

print("Starting button sensory loop...")
pressed_buttons = set()

#pygame.mixer.pre_init(44100,16,2,4096)
pygame.init()
pygame.mixer.init()

#init pydub stuff
loop1 = AudioSegment.from_wav("/home/pi/Final/loop1.wav")

loop2 = AudioSegment.from_wav("/home/pi/Final/loop2.wav")

length = len(loop1)

mixed = loop2[:length].overlay(loop1)

#set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def GPIO27_callback(channel):
    exit(0)
    print(27)
    
def GPIO19_callback(channel):
    print("callback 19")
    cmd1 = 'arecord -D hw:1,0 -d 5 -f S24_3LE /home/pi/Final/loop1.wav -c2 -r48000 &'
    os.system(cmd1)

def GPIO26_callback(channel):
    print("callback 26")
    cmd2 = 'arecord -D hw:1,0 -d 5 -f S24_3LE /home/pi/Final/loop2.wav -c2 -r48000 &'
    os.system(cmd2)

GPIO.add_event_detect(27,GPIO.FALLING, callback=GPIO27_callback)
GPIO.add_event_detect(19,GPIO.FALLING, callback=GPIO19_callback)
GPIO.add_event_detect(26,GPIO.FALLING, callback=GPIO26_callback)


while True:
    # Make sure to take a break during each trellis.read_buttons
    # cycle.
    time.sleep(0.1)
    
    just_pressed, released = trellis.read_buttons()
    for b in just_pressed:
        name = '/home/pi/Final' + paths[3] + wavefiles[b]
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(name))
        #pygame.mixer.music.load(name)
        #pygame.mixer.music.play(0)
        print("pressed:", b)
        trellis.led[b] = True
    pressed_buttons.update(just_pressed)
    for b in released:
        print("released:", b)
        trellis.led[b] = False
    pressed_buttons.difference_update(released)
    for b in pressed_buttons:
        print("still pressed:", b)
        trellis.led[b] = True

    loop1 = AudioSegment.from_wav("/home/pi/Final/loop1.wav")

    loop2 = AudioSegment.from_wav("/home/pi/Final/loop2.wav")

    length = len(loop1)

    mixed = loop2[:length].overlay(loop1)
    
    play(mixed)