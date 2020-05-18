import pygame
import time
import busio
from board import SCL, SDA
from adafruit_trellis import Trellis
from pygame.locals import *   # for event MOUSE variables
import RPi.GPIO as GPIO
import pyaudio
import wave
import setting   # import global variables


# Create the I2C interface
i2c = busio.I2C(SCL, SDA)

# Create a Trellis object
trellis = Trellis(i2c)  # 0x70 when no I2C address is supplied

# 'auto_show' defaults to 'True', so anytime LED states change,
# the changes are automatically sent to the Trellis board. If you
# set 'auto_show' to 'False', you will have to call the 'show()'
# method afterwards to send updates to the Trellis board.

print("Starting button sensory loop...")
pressed_buttons = set()

#pygame.mixer.pre_init(44100,16,2,4096)
pygame.init()
pygame.mixer.init()


#button interrupts
GPIO.setmode(GPIO.BCM)

#initialize playback buttons

GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)


state19 = setting.state1
state26 = setting.state2

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
    

GPIO.add_event_detect(19,GPIO.FALLING, callback=GPIO19_callback)
GPIO.add_event_detect(26,GPIO.FALLING, callback=GPIO26_callback)

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



wavefiles = ['01.wav','02.wav','03.wav','04.wav','05.wav','06.wav','07.wav','08.wav',
  '09.wav','10.wav','11.wav','12.wav','13.wav','14.wav','15.wav','16.wav']
path = '/home/pi/Final/drums2/'
while True:
    # Make sure to take a break during each trellis.read_buttons
    # cycle.
    time.sleep(0.1)
    
    just_pressed, released = trellis.read_buttons()
    for b in just_pressed:
        name = path+wavefiles[b]
        #pygame.mixer.Sound.load(name)
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(name))
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