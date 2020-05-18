#writes to synthesis_fifo stored in Final

import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *   # for event MOUSE variables
import os
#import setting   # import global variables

os.putenv('SDL_VIDEODRIVER', 'fbcon')   # Display on piTFT
os.putenv('SDL_FBDEV', '/dev/fb1')     
os.putenv('SDL_MOUSEDRV', 'TSLIB')     # Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

#pygame stuff
pygame.init()
pygame.mouse.set_visible(False)
WHITE = 255, 255, 255
BLACK = 0,0,0
GREEN = 0, 128, 0
RED = 255, 0, 0
CYAN = 109, 237, 226 #for background of TFT screen
screen = pygame.display.set_mode((320, 240))
my_font= pygame.font.Font(None, 30)
other_font= pygame.font.Font(None, 20)

GPIO.setmode(GPIO.BCM)

GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#list of instrument values communicated via fifo
#change values to match frequency value to be communicated

instrument_buttons = ['piano', 'cello', 'guitar', 'flute', 'drum']

instrument_index = 0    #piano default

button_states = ['stopped', 'recording', 'playback']

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

#exit loop
#end = False
stopped = False

loopcount = 0 #counts amount of loops
timecount = 0 #timer variable

    
def GPIO27_callback(channel):
    exit(0)
    print(27)
    
#def GPIO19_callback(channel):
    #print(19)
    
#def GPIO26_callback(channel):
    #print(26)
    
GPIO.add_event_detect(27,GPIO.FALLING, callback=GPIO27_callback)
#GPIO.add_event_detect(19,GPIO.FALLING, callback=GPIO19_callback)
#GPIO.add_event_detect(26,GPIO.FALLING, callback=GPIO26_callback)

#main loop
while True:
    time.sleep(0.02)
    
    loopcount = loopcount + 1
    if loopcount == 50: #1 second has passed
        timecount = timecount + 1
        loopcount = 0
    
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
                if(instrument_index == 4): #out of bounds
                    instrument_index = 0
                else:
                    instrument_index = instrument_index + 1

                print('up arrow')
                print(instrument_index)
                print(instrument_buttons[instrument_index])
            elif y > 170 and y < 200 and x > 60 and x < 100: #if down arrow
                if(instrument_index == 0): #out of bounds
                    instrument_index = 4
                else:
                    instrument_index = instrument_index - 1
                print('down arrow')
                print(instrument_index)
                print(instrument_buttons[instrument_index])
        
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
                
   
GPIO.cleanup()
pygame.quit()
