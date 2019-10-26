
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

    def __init__(self):
        self.serial_port = threaded_serial.SerialPort()
        self.data = []
        self.input_callback = None

    def open(self, input_callback, port_name=None, baud=38400):
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
        while len(self.data) >= 7:
            if (self.data[0] == 0xF0) and (self.data[6] == 0x0F):
                in_data = {
                    'touch': self.data[1],
                    'gpio': self.data[2],
                    'dist1': self.data[3],
                    'dist2': self.data[4],
                    'dist3': self.data[5]
                }
                print in_data
                if self.input_callback:
                    self.input_callback(in_data)
                self.data = []
            else:
                self.data = self.data[1:]

    def close(self):
        self.serial_port.close()


class SoundMachine(object):
    last_touch = 0
    def Open(self):
        return fluidsynth.init('/usr/share/sounds/sf2/FluidR3_GM.sf2', "alsa")
    def on_input(self, in_dict):
        # get touch keys
        touch = in_dict['touch']
        delta_touch = touch^self.last_touch
        self.last_touch = touch
        if (delta_touch & 0x01):
            if (touch & 0x01):
                fluidsynth.play_Note(ord('A'), 0, 100)
            else:
                fluidsynth.stop_Note(ord('A'), 0)
        if (delta_touch & 0x02):
            if (touch & 0x02):
                fluidsynth.play_Note(ord('B'), 0, 100)
            else:
                fluidsynth.stop_Note(ord('B'), 0)
        if (delta_touch & 0x04):
            if (touch & 0x04):
                fluidsynth.play_Note(ord('C'), 0, 100)
            else:
                fluidsynth.stop_Note(ord('C'), 0)
        if (delta_touch & 0x08):
            if (touch & 0x08):
                fluidsynth.play_Note(ord('D'), 0, 100)
            else:
                fluidsynth.stop_Note(ord('D'), 0)
        if (delta_touch & 0x10):
            if (touch & 0x10):
                fluidsynth.play_Note(ord('E'), 0, 100)
            else:
                fluidsynth.stop_Note(ord('E'), 0)
        if (delta_touch & 0x20):
            if (touch & 0x20):
                fluidsynth.play_Note(ord('F'), 0, 100)
            else:
                fluidsynth.stop_Note(ord('F'), 0)
        if (delta_touch & 0x40):
            if (touch & 0x40):
                fluidsynth.play_Note(ord('G'), 0, 100)
            else:
                fluidsynth.stop_Note(ord('G'), 0)

        dist1 = in_dict['dist3']
        if (dist1 < 180):
            dist1_note = Note();
            dist1_note.from_int(in_dict['dist3']/2)
            fluidsynth.play_Note(dist1_note,1, 20)
            

    def run(self):
        #takes the main loop and runs background tasks
        insturment = 1
        while 1:
            time.sleep(2)
            fluidsynth.set_instrument(0,insturment)
            insturment+=1
            if (insturment>50):
                return


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
        #time.sleep(60)

    input.close()


if __name__ == "__main__":
    main()