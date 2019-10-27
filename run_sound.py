
import sys
sys.path.append("..")

import time
import serial
import serial.tools.list_ports
import threading
import threaded_serial

#https://stackoverflow.com/questions/6487180/synthesize-musical-notes-with-piano-sounds-in-python
from mingus.core import notes, chords
from mingus.containers import *
from mingus.midi import fluidsynth



class InputInterface():
    last_touch = [1024]*7
    threshold = 25

    def __init__(self):
        self.serial_port = threaded_serial.SerialPort()
        self.data = []
        self.input_callback = None

    def open(self, input_callback, port_name=None, baud=256000):
        self.input_callback = input_callback
        if not port_name:
            port_list = serial.tools.list_ports.comports()
            print port_list
            for p in port_list:
                print p.description
                if "USBUART" in p.description:
                    port_name = p.device

        self.serial_port.open(port_name, baud, self.serial_receive)

    def serial_receive(self, data):
        self.data = self.data + data
        while len(self.data) >= 20:
            if (self.data[0] == 0xF0) and (self.data[19] == 0x0F):
                touch_in = [self.data[x]&0xFF+(self.data[x+1]>>8) for x in range(5,19,2)]
                delta_touch = [(touch_in[x]-self.last_touch[x]) > self.threshold for x in range(7)]
                #print touch_in, self.last_touch, delta_touch
                self.last_touch = touch_in
                in_data = {
                    'gpio': self.data[1],
                    'dist1': self.data[2],
                    'dist2': self.data[3],
                    'dist3': self.data[4],
                    'touch': delta_touch
                }
                #print in_data
                if self.input_callback:
                    self.input_callback(in_data)
                self.data = []
            else:
                self.data = self.data[1:]

    def close(self):
        self.serial_port.close()


class SoundMachine(object):
    last_touch = [False]*7
    dist1_notes = []
    dist2_notes = []
    def Open(self):
        fluidsynth.init('/usr/share/sounds/sf2/FluidR3_GM.sf2', "alsa")
        fluidsynth.set_instrument(0, 6)
        fluidsynth.set_instrument(1, 4)

    def on_input(self, in_dict):
        # get touch keys
        touch = in_dict['touch']
        note_list = [('G',4), ('F',4), ('E',4), ('D',4), ('C',4), ('B',3), ('A',3)]
        for x in range(len(touch)):
            #print x, touch[x]
            if touch[x] and not self.last_touch[x]:
                #print note_list[x]
                fluidsynth.play_Note(Note(note_list[x][0],note_list[x][1]), 0, 100)
        self.last_touch = touch

        #print in_dict['dist1'], in_dict['dist2'], in_dict['dist3']
        dist = in_dict['dist1']
        if (dist < 150):
            if (len(self.dist1_notes)>20):
                fluidsynth.stop_Note(self.dist1_notes[0], 1)
                self.dist1_notes = self.dist1_notes[1:]
            dist1_note = Note()
            dist1_note.from_int(dist/2)
            fluidsynth.play_Note(dist1_note, 1, 80)
            self.dist1_notes.append(dist1_note)
        else:
            for note in self.dist1_notes:
                fluidsynth.stop_Note(note, 1)
            self.dist1_notes = []

        dist = in_dict['dist2']
        if (dist < 150):
            if (len(self.dist1_notes)>20):
                fluidsynth.stop_Note(self.dist2_notes[0], 1)
                self.dist2_notes = self.dist2_notes[1:]
            dist_note = Note()
            dist_note.from_int(dist / 2)
            fluidsynth.play_Note(dist_note, 2, 80)
            self.dist2_notes.append(dist_note)
        else:
            for note in self.dist2_notes:
                fluidsynth.stop_Note(note, 2)
            self.dist2_notes = []

        #TODO use distance 3 to play music from file


    def run(self):
        #takes the main loop and runs background tasks
        insturment = 15
        while 1:
            time.sleep(10)
            print "instrument {0}".format(insturment)
            fluidsynth.set_instrument(2,insturment)
            insturment+=1
            if (insturment>70):
                insturment = 0


def test_input(in_dict):
    print in_dict

def main():

    if 0:
        input = InputInterface()
        input.open(test_input)
        time.sleep(120)
    else:
        sound_machine = SoundMachine()
        sound_machine.Open()
        input = InputInterface()
        input.open(sound_machine.on_input)
        sound_machine.run()

    input.close()


if __name__ == "__main__":
    main()