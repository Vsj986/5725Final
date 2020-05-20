from pydub import AudioSegment
from pydub.playback import play
# Download an audio file
#urllib.request.urlretrieve("https://tinyurl.com/wx9amev", "metallic-drums.wav")
# Load into PyDub
loop1 = AudioSegment.from_wav("/home/pi/Final/loop1.wav")

loop2 = AudioSegment.from_wav("/home/pi/Final/loop2.wav")

length = len(loop1)

mixed = loop2[:length].overlay(loop1)
# Play the result
play(mixed)