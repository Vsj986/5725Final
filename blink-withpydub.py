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

#os.putenv('SDL_VIDEODRIVER', 'fbcon')   # Display on piTFT
#os.putenv('SDL_FBDEV', '/dev/fb1')     
os.putenv('SDL_MOUSEDRV', 'TSLIB')     # Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

#initialize pygame and tft
pygame.init()
pygame.mouse.set_visible(True)
WHITE = 255, 255, 255
BLACK = 0,0,0
GREEN = 0, 128, 0
RED = 255, 0, 0
CYAN = 109, 237, 226 #for background of TFT screen
screen = pygame.display.set_mode((320, 240))
my_font= pygame.font.Font(None, 30)
other_font= pygame.font.Font(None, 20)


# Create the I2C interface
i2c = busio.I2C(SCL, SDA)
# Create a Trellis object
trellis = Trellis(i2c)  # 0x70 when no I2C address is supplied


# instrument files
wavefiles = ['01.wav','02.wav','03.wav','04.wav','05.wav','06.wav','07.wav','08.wav',
  '09.wav','10.wav','11.wav','12.wav','13.wav','14.wav','15.wav','16.wav']

inst = setting.index   # instrument index
paths = ['/piano/','/violin/','/piano/','/flute/','/drum/']

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

#initialize the screen
instrument_buttons = ['piano', 'violin', 'flute', 'drum']
instrument_index = 0    #piano default
button_states = ['stopped', 'recording', 'playback']

global state1
global state2
state1 = 0
state2 = 0

my_buttons= {(80,120):instrument_buttons[instrument_index], (270,200):'quit', 
                (200,100): button_states[state1], (200,120): button_states[state2]}

screen.fill(CYAN)               # Erase the Work space     
for text_pos, my_text in my_buttons.items():    
    text_surface = other_font.render(my_text, True, WHITE)    
    rect = text_surface.get_rect(center=text_pos)
    screen.blit(text_surface, rect)
    
pygame.draw.polygon(screen, WHITE, ((80,50),(70,60),(90,60))) #up arrow
pygame.draw.polygon(screen, WHITE, ((80,190),(70,180),(90,180))) #down arrow
pygame.display.flip()

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

# set up GPIO callback functions
def GPIO27_callback(channel):
    exit(0)
    print(27)
    
def GPIO19_callback(channel):
    print("callback 19")
    cmd1 = 'arecord -D hw:1,0 -d 5 -f S24_3LE /home/pi/Final/loop1.wav -c2 -r48000 &'
    os.system(cmd1)
    ################## see if buttons get updated
    my_buttons[(200,100)] = "testing"
    print("19_my buttons:",my_buttons)

def GPIO26_callback(channel):
    print("callback 26")
    cmd2 = 'arecord -D hw:1,0 -d 5 -f S24_3LE /home/pi/Final/loop2.wav -c2 -r48000 &'
    os.system(cmd2)
    ################## see if buttons get updated
    my_buttons[(200,120)] = "testing"
    print("19_my buttons:",my_buttons)

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
    
    #change GUI
    for event in pygame.event.get():        
        if(event.type is MOUSEBUTTONDOWN):            
            pos = pygame.mouse.get_pos()
            screen.fill(CYAN)
            for text_pos, my_text in my_buttons.items():    
                text_surface = other_font.render(my_text, True, WHITE)    
                rect = text_surface.get_rect(center=text_pos)
                screen.blit(text_surface, rect)
            pygame.draw.polygon(screen, WHITE, ((80,50),(70,60),(90,60))) #up arrow
            pygame.draw.polygon(screen, WHITE, ((80,190),(70,180),(90,180))) #down arrow
        elif(event.type is MOUSEBUTTONUP):            
            pos = pygame.mouse.get_pos() 
            x,y = pos
            if y > 190 and y < 210 and x > 250 and x < 290: #if quit button           
                exit(0)
            elif y > 40 and y < 70 and x > 60 and x < 100: #if up arrow
                if(instrument_index == 3): #out of bounds
                    instrument_index = 0
                else:
                    instrument_index = instrument_index + 1

                print('up arrow')
                print(instrument_index)
                print(instrument_buttons[instrument_index])
            elif y > 170 and y < 200 and x > 60 and x < 100: #if down arrow
                if(instrument_index == 0): #out of bounds
                    instrument_index = 3
                else:
                    instrument_index = instrument_index - 1
                print('down arrow')
                print(instrument_index)
                print(instrument_buttons[instrument_index])
            
    # update record buttons
    
    # updating the screen when a record button is pressed
    if GPIO.input(19) == GPIO.LOW or GPIO.input(26) == GPIO.LOW:
        print("line 188")
        print("line 189, my buttons: ", my_buttons)
        screen.fill(CYAN)
        pygame.draw.polygon(screen, WHITE, ((80,50),(70,60),(90,60))) #up arrow
        pygame.draw.polygon(screen, WHITE, ((80,190),(70,180),(90,180))) #down arrow
                    
        #my_buttons= {(80,120):instrument_buttons[instrument_index], (270,200):'quit',
        #            (200,100): button_states[state1], (200,120): button_states[state2]}

        for text_pos, my_text in my_buttons.items():    
            text_surface = other_font.render(my_text, True, WHITE)    
            rect = text_surface.get_rect(center=text_pos)
            screen.blit(text_surface, rect)
        pygame.display.flip()
             
    else:
        screen.fill(CYAN)
        pygame.draw.polygon(screen, WHITE, ((80,50),(70,60),(90,60))) #up arrow
        pygame.draw.polygon(screen, WHITE, ((80,190),(70,180),(90,180))) #down arrow
                    
        my_buttons= {(80,120):instrument_buttons[instrument_index], (270,200):'quit',
                        (200,100): button_states[state1], (200,120): button_states[state2]}

        for text_pos, my_text in my_buttons.items():    
            text_surface = other_font.render(my_text, True, WHITE)    
            rect = text_surface.get_rect(center=text_pos)
            screen.blit(text_surface, rect)
        pygame.display.flip()
        
        
    # mixing channel 1 and 2 together
    loop1 = AudioSegment.from_wav("/home/pi/Final/loop1.wav")

    loop2 = AudioSegment.from_wav("/home/pi/Final/loop2.wav")

    length = len(loop1)

    mixed = loop2[:length].overlay(loop1)
    
    print("playing mixed")
    play(mixed)