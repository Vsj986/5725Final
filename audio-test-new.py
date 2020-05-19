import os
import time


#record audio
#cmd1='arecord -D hw:1,0 -d 5 -f cd /home/pi/Final/osaudiotest.wav -r 48000 -c 1 &'

cmd1 = 'arecord -D hw:1,0 -d 5 -f S24_3LE /home/pi/Final/osaudiotest.wav -c2 -r48000 &'
os.system(cmd1)
print("recording...")