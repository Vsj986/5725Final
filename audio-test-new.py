import os
import time
import pygame
from pygame.locals import *   # for event MOUSE variables

pygame.init()

#record audio
cmd1='arecord -D hw:1,0 -d 5 -f cd /home/pi/Final/osaudiotest.wav -r 48000 -c 1 &'
os.system(cmd1)
print("recording...")