
import sys
sys.path.append("..")

import time
import serial
import serial.tools.list_ports
import threading
import threaded_serial




class InputInterface():

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
                in_data = {
                    'gpio': self.data[1],
                    'dist1': self.data[2],
                    'dist2': self.data[3],
                    'dist3': self.data[4],
                    'touch': [self.data[x]&0xFF+(self.data[x+1]>>8) for x in range(5,19,2)]
                }
                print in_data
                if self.input_callback:
                    self.input_callback(in_data)
                self.data = []
            else:
                self.data = self.data[1:]

    def close(self):
        self.serial_port.close()

#
# class SoundMachine(object):
#     last_touch = 0
#     def Open(self):
#         return fluidsynth.init('/usr/share/sounds/sf2/FluidR3_GM.sf2', "alsa")
#     def on_input(self, in_dict):
#         # get touch keys
#         touch = in_dict['touch']
#         delta_touch = touch^self.last_touch
#         self.last_touch = touch
#         if (delta_touch & 0x01):
#             if (touch & 0x01):
#                 fluidsynth.play_Note(ord('A'), 0, 100)
#             else:
#                 fluidsynth.stop_Note(ord('A'), 0)
#         if (delta_touch & 0x02):
#             if (touch & 0x02):
#                 fluidsynth.play_Note(ord('B'), 0, 100)
#             else:
#                 fluidsynth.stop_Note(ord('B'), 0)
#         if (delta_touch & 0x04):
#             if (touch & 0x04):
#                 fluidsynth.play_Note(ord('C'), 0, 100)
#             else:
#                 fluidsynth.stop_Note(ord('C'), 0)
#         if (delta_touch & 0x08):
#             if (touch & 0x08):
#                 fluidsynth.play_Note(ord('D'), 0, 100)
#             else:
#                 fluidsynth.stop_Note(ord('D'), 0)
#         if (delta_touch & 0x10):
#             if (touch & 0x10):
#                 fluidsynth.play_Note(ord('E'), 0, 100)
#             else:
#                 fluidsynth.stop_Note(ord('E'), 0)
#         if (delta_touch & 0x20):
#             if (touch & 0x20):
#                 fluidsynth.play_Note(ord('F'), 0, 100)
#             else:
#                 fluidsynth.stop_Note(ord('F'), 0)
#         if (delta_touch & 0x40):
#             if (touch & 0x40):
#                 fluidsynth.play_Note(ord('G'), 0, 100)
#             else:
#                 fluidsynth.stop_Note(ord('G'), 0)
#
#         # dist1 = in_dict['dist3']
#         # if (dist1 < 180):
#         #     dist1_note = Note();
#         #     dist1_note.from_int(in_dict['dist3']/2)
#         #     fluidsynth.play_Note(dist1_note, 20)
#
#
#     def run(self):
#         #takes the main loop and runs background tasks
#         insturment = 1
#         while 1:
#             time.sleep(600)
#             print "instrument {0}".format(insturment)
#             fluidsynth.set_instrument(0,insturment)
#             insturment+=1
#             if (insturment>50):
#                 return


def test_input(in_dict):
    print in_dict

def main():
    if 0:
        input = InputInterface()
        input.open(test_input)
        time.sleep(120)
    else:
        input = InputInterface()
        input.open(test_input)
        time.sleep(60)

    input.close()


if __name__ == "__main__":
    main()