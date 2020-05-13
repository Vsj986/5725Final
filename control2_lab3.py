import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *   # for event MOUSE variables
import os

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
screen = pygame.display.set_mode((320, 240))
my_font= pygame.font.Font(None, 30)
other_font= pygame.font.Font(None, 20)

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT) #connected to servos
GPIO.setup(5, GPIO.OUT)

GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

my_buttons= {(160,120):'stop', (270,200):'quit'}
screen.fill(BLACK)               # Erase the Work space     
for text_pos, my_text in my_buttons.items():    
    text_surface = my_font.render(my_text, True, WHITE)    
    rect = text_surface.get_rect(center=text_pos)
    screen.blit(text_surface, rect)
    
pygame.draw.circle(screen, RED, (160,120), 30)
    
pygame.display.flip()

#exit loop
#end = False
stopped = False

loopcount = 0 #counts amount of loops
timecount = 0 #timer variable

pos1 = (70, 90) #positions of the text
pos2 = (70, 120)
pos3 = (70, 150)
pos4 = (240, 90)
pos5 = (240, 120)
pos6 = (240, 150)

timepos1 = (100, 90) #positions of the times
timepos2 = (100, 120)
timepos3 = (100, 150)
timepos4 = (270, 90)
timepos5 = (270, 120)
timepos6 = (270, 150)

dictleft = {pos1: 'empty', pos2: 'empty', pos3: 'empty'}
dictright = {pos4: 'empty', pos5: 'empty', pos6: 'empty'}

timeleft = {timepos1: '0', timepos2: '0', timepos3: '0'}
timeright = {timepos4: '0', timepos5: '0', timepos6: '0'}

pw_cal= 0.0015
pw_cw= 0.0013
pw_ccw= 0.0017
dur = 0.02
period_cal= dur + pw_cal
freq_cal = 1/period_cal
dc_cal = pw_cal/period_cal*100
p1 = GPIO.PWM(5, freq_cal)
p2 = GPIO.PWM(6, freq_cal)
def GPIO22_callback(channel):
    if stopped == False:
        #print(22)
        control(p1,'cw')
    
def GPIO27_callback(channel):
    if stopped == False:
        #print(27)
        control(p1,'stop')
    
def GPIO17_callback(channel):
    if stopped == False:
        #print(17)
        control(p1,'ccw')
    
def GPIO23_callback(channel):
    if stopped == False:
        #print(23)
        control(p2,'cw')
    
def GPIO19_callback(channel):
    if stopped == False:
        #print(19)
        control(p2,'stop')
    
def GPIO26_callback(channel):
    if stopped == False:
        #print(26)
        control(p2,'ccw')
    
GPIO.add_event_detect(22,GPIO.FALLING, callback=GPIO22_callback)
GPIO.add_event_detect(27,GPIO.FALLING, callback=GPIO27_callback)
GPIO.add_event_detect(17,GPIO.FALLING, callback=GPIO17_callback)
GPIO.add_event_detect(23,GPIO.FALLING, callback=GPIO23_callback)
GPIO.add_event_detect(19,GPIO.FALLING, callback=GPIO19_callback)
GPIO.add_event_detect(26,GPIO.FALLING, callback=GPIO26_callback)



# control(6,'stop')
#p = GPIO.PWM(servo_pin, freq_cal)

def control(p, direction):
    pw_cal= 0.0015
    pw_cw= 0.0013
    pw_ccw= 0.0017
    p.start(0)
    #print('start')
    
    #update dictionary
    if p == p1: #left
        dictleft[pos1] = dictleft[pos2]
        dictleft[pos2] = dictleft[pos3]
        dictleft[pos3] = direction
        
        timeleft[timepos1] = timeleft[timepos2]
        timeleft[timepos2] = timeleft[timepos3]
        timeleft[timepos3] = str(timecount)
        
        
    if p == p2: #right
        dictright[pos4] = dictright[pos5]
        dictright[pos5] = dictright[pos6]
        dictright[pos6] = direction
        
        timeright[timepos4] = timeright[timepos5]
        timeright[timepos5] = timeright[timepos6]
        timeright[timepos6] = str(timecount)
    
    if direction == 'stop':
        p.ChangeDutyCycle(0)
    elif direction == 'cw':
        pw = pw_cw
        dc = pw/(pw+0.02)*100
        period = pw + 0.02
        freq = 1/period
        print(dc, freq)
        p.ChangeDutyCycle(dc)
        p.ChangeFrequency(freq)
    elif direction == 'ccw':
        pw = pw_ccw
        dc = pw/(pw+0.02)*100
        period = pw + 0.02
        freq = 1/period
        print(dc, freq)
        p.ChangeDutyCycle(dc)
        p.ChangeFrequency(freq)
        
while True:
    time.sleep(0.02)
    
    loopcount = loopcount + 1
    if loopcount == 50: #1 second has passed
        timecount = timecount + 1
        loopcount = 0
    
    for event in pygame.event.get():        
        if(event.type is MOUSEBUTTONDOWN):            
            pos = pygame.mouse.get_pos()
            screen.fill(BLACK)
            for text_pos, my_text in my_buttons.items():    
                text_surface = my_font.render(my_text, True, WHITE)    
                rect = text_surface.get_rect(center=text_pos)
                screen.blit(text_surface, rect)
        elif(event.type is MOUSEBUTTONUP):            
            pos = pygame.mouse.get_pos() 
            x,y = pos
            if y > 190 and y < 210 and x > 250 and x < 290: #if quit button           
                exit(0)
            elif y > 110 and y < 130 and x > 140 and x < 180: #if stop button
                if stopped == False: #we are trying to stop it
                    stopped = True #we have stopped it
                    #change the text to "resume" idk how to do that tho
                    my_buttons[(160,120)] = 'resume'
                    control(p1,'stop')
                    control(p2,'stop')
                elif stopped == True:
                    stopped = False
                    my_buttons[(160,120)] = 'stop'
                    control(p1, dictleft[pos2])
                    control(p2, dictright[pos5]) #go back to previous states
        
    screen.fill(BLACK)
    if stopped == True:
        pygame.draw.circle(screen, GREEN, (160,120), 30)
    else:
        pygame.draw.circle(screen, RED, (160,120), 30)
        
    for left_text_positions, left_text in dictleft.items():    
        left_text_surface = other_font.render(left_text, True, WHITE)    
        left_rect = left_text_surface.get_rect(center=left_text_positions)
        screen.blit(left_text_surface, left_rect)
            
    for right_text_positions, right_text in dictright.items():    
        right_text_surface = other_font.render(right_text, True, WHITE)    
        right_rect = right_text_surface.get_rect(center=right_text_positions)
        screen.blit(right_text_surface, right_rect)
            
    for left_time_positions, left_time in timeleft.items():    
        left_time_surface = other_font.render(left_time, True, WHITE)    
        left_time_rect = left_time_surface.get_rect(center=left_time_positions)
        screen.blit(left_time_surface, left_time_rect)
            
    for right_time_positions, right_time in timeright.items():    
        right_time_surface = other_font.render(right_time, True, WHITE)    
        right_time_rect = right_time_surface.get_rect(center=right_time_positions)
        screen.blit(right_time_surface, right_time_rect)
            
    for text_pos, my_text in my_buttons.items():    
        text_surface = my_font.render(my_text, True, WHITE)    
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface, rect)
                
    pygame.display.flip()
                
   
GPIO.cleanup()
