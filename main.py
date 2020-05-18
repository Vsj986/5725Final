#writes to synthesis_fifo stored in Final

import RPi.GPIO as GPIO
import time
import pygame
from pygame.locals import *   # for event MOUSE variables
import os
import busio
from board import SCL, SDA
from adafruit_trellis import Trellis
import pyaudio #these are for audio recording
import wave
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

# Create the I2C interface
i2c = busio.I2C(SCL, SDA)

# Create a Trellis object
trellis = Trellis(i2c)  # 0x70 when no I2C address is supplied

GPIO.setmode(GPIO.BCM)

GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

#button callbacks
def GPIO27_callback(channel):
    exit(0)
    print(27)
    
def GPIO19_callback(channel):
    print("19")

    state19 = state19 + 1 #increase state each time it is pressed
    if state19 > 2:
        state19 = 0#reset back to state 0


    if state19 == 0: #empty state
        #stop sounds if playing
        print('state0-19')
        pygame.mixer.Channel(1).stop()
    elif state19 == 1: #record
        print('record19')
        record('19')
    elif state19 == 2; #playback
        print('playback19')
        playback('19', 1)
    
def GPIO26_callback(channel):
    print("26")

    state26 = state26 + 1 #increase state each time it is pressed
    if state26 > 2:
        state26 = 0#reset back to state 0


    if state26 == 0: #empty state
        #stop sounds if playing
        print('state0-26')
        pygame.mixer.Channel(2).stop()
    elif state26 == 1: #record
        print('record26')
        record('26')
    elif state26 == 2; #playback
        print('playback26')
        playback('26', 2)

    
GPIO.add_event_detect(27,GPIO.FALLING, callback=GPIO27_callback)
GPIO.add_event_detect(19,GPIO.FALLING, callback=GPIO19_callback)
GPIO.add_event_detect(26,GPIO.FALLING, callback=GPIO26_callback)

#record and playback

def record(buttonNum):
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 4096 # 2^12 samples for buffer
    record_secs = 3 # seconds to record
    dev_index = 2 # device index found by p.get_device_info_by_index(ii)
    wav_output_filename = '/home/pi/Final/record'+buttonNum+'.wav' # name of .wav file

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

def playback(buttonNum, chan): #(string, int)
    pygame.mixer.Channel(chan).play(pygame.mixer.Sound('/home/pi/Final/record'+buttonNum+'.wav'), -1)
    #loop indefinitely

    #this is where we would read the potentiometer value to see how long we play the file before looping


#blinkatest stuff
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
pygame.mixer.init()

wavefiles = ['01.wav','02.wav','03.wav','04.wav','05.wav','06.wav','07.wav','08.wav',
  '09.wav','10.wav','11.wav','12.wav','13.wav','14.wav','15.wav','16.wav']

paths = ['/piano/','/violin/','/piano/','/flute/','/drum/']

#main loop
while True:
    time.sleep(0.02)
    #timer
    loopcount = loopcount + 1
    if loopcount == 50: #1 second has passed
        timecount = timecount + 1
        loopcount = 0

    #audio stuff from blinkatest
    just_pressed, released = trellis.read_buttons()
    for b in just_pressed:
        name = '/home/pi/Final' + paths[instrument_index] + wavefiles[b]
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