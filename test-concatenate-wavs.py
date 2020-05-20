import os
import time
from pydub import AudioSegment
from pydub.playback import play
import pygame
import time
import busio
from board import SCL, SDA
from adafruit_trellis import Trellis
from pygame.locals import *   # for event MOUSE variables
#import setting

# Create the I2C interface
i2c = busio.I2C(SCL, SDA)

# Create a Trellis object
trellis = Trellis(i2c)  # 0x70 when no I2C address is supplied


#working concatenation code
#this worked on my mac at least lol i just added in the path stuff
# instrument files
wavefiles = ['01.wav','02.wav', '03.wav', '04.wav','05.wav', '06.wav', '07.wav','08.wav', 
			'09.wav', '10.wav','11.wav', '12.wav', '13.wav','14.wav', '15.wav', '16.wav']

path = "/home/pi/final/violin/" #I tested using violin sounds

#testing concatenation once
'''
combined = AudioSegment.from_wav(path + wavefiles[0])

for wav in wavefiles[1:]:
    combined += AudioSegment.from_wav(path + wav)

play(combined)'''

print("Starting button sensory loop...")
pressed_buttons = set()

#pygame.mixer.pre_init(44100,16,2,4096)
pygame.init()
pygame.mixer.init()

#def concatenate_wav():
	#wavs = [AudioSegment.from_wav(wav['path']) for wav in wavset]

while True:
    # Make sure to take a break during each trellis.read_buttons
    # cycle.
    time.sleep(0.1)
    
    just_pressed, released = trellis.read_buttons()
    combined = AudioSegment.from_wav(path + wavefiles[0])
    for b in just_pressed:
        combined += AudioSegment.from_wav(path + wavefiles[b]) #add pressed file to concatenation
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

    play(combined)









