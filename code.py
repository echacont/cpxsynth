# cpx synth
# Eleonora Chacon Taylor

import board
import array
import time
import math
import digitalio
import audiocore
import audioio
import usb_midi
import adafruit_midi
from adafruit_midi.midi_message     import note_parser
from adafruit_midi.note_on          import NoteOn
from adafruit_midi.note_off         import NoteOff
from adafruit_midi.control_change   import ControlChange

## Constants

### 440Hz is the standard frequency for A4 (A above middle C)
### MIDI defines middle C as 60 and modulation wheel is cc 1 by convention
A4refhz = 440
midi_note_A4 = note_parser("A4")

sampleRate = 16000

## Functions

### simple frequency modulation synthesis
def fmwave0(cfreq, ratio, index, sampleRate=sampleRate):
    if (cfreq < sampleRate//2):
        length = math.trunc(sampleRate/cfreq)
        Tsample = math.pow(sampleRate, -1)
        wavearray = array.array("H", [0] * length)
        for i in range(length):
            t = i*Tsample
            carrierPhase = cfreq*2*math.pi*t
            modPhase     = index*math.cos(ratio*carrierPhase)
            a = math.sin(carrierPhase+modPhase)
            sample = math.trunc(((a+1)/2) * math.pow(2,15))
            wavearray[i] = sample
    else:
        wavearray = array.array("H", [0])

    return audiocore.RawSample(wavearray, sample_rate=sampleRate)

### Calculate the note frequency from the midi_note with pitch bend
### of pb_st (float) semitones
### Returns float
def note_frequency(midi_note, pb_st):
    # 12 semitones in an octave
    return A4refhz * math.pow(2, (midi_note - midi_note_A4 + pb_st) / 12.0)

## Setup the system

### Turn the speaker on
#speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
#speaker_enable.direction = digitalio.Direction.OUTPUT
#speaker_enable.value = True

### Create AudioOut object using the speaker pin
dac = audioio.AudioOut(board.SPEAKER)

### MIDI setup
### midi channel 1
midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0],
                          in_channel=0)

## welcome
print("cpx synth: listening to channel 1")

### control change initial values
cc14 = 0        # FM ratio
cc15 = 0        # FM index
last_note = midi_note_A4
note_freq = note_frequency(last_note,0)
### main FM parameters
ratio = 1
index = 1

## Synth control
while(True):
    msg = midi.receive()
    if isinstance(msg, NoteOn) and msg.velocity != 0:
        last_note = msg.note
        note_freq = note_frequency(last_note,0)             # 0 pitch bend
        #wave_vol = msg.velocity/127.00001
        #print("NoteOn received: %d" % last_note)
        wave = fmwave0(note_freq, ratio, index, sampleRate)
        dac.play(wave, loop=True)

    elif isinstance(msg, ControlChange):
        ### control change number 14: FM ratio
        if msg.control == 14:
            cc14 = msg.value  # msg.value is 0 (none) to 127 (max)
            ratio = math.trunc(16 * cc14/127.00001)
            print("CC14: = %d" % ratio)
            wave = fmwave0(note_freq, ratio, index, sampleRate)
            if dac.playing:
                dac.play(wave, loop=True)

        ### control change number 15: FM index
        if msg.control == 15:
            cc15 = msg.value  # msg.value is 0 (none) to 127 (max)
            index = 15.999 * cc15/127.00001
            print("CC15: = %0.3f" % index)
            wave = fmwave0(note_freq, ratio, index, sampleRate)
            if dac.playing:
                dac.play(wave, loop=True)


    elif (isinstance(msg, NoteOff) or
          (isinstance(msg, NoteOn) and msg.velocity == 0)):
        dac.stop()

