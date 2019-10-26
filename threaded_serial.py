
import serial
import threading
import sys
import serial.tools.list_ports
import time


class SerialPort(object):
    def __init__(self):
        self.serial_port = None
        self.active = False
        self.receive_callback = None
        self.thread = None

    def open(self, port_name = None, baud_rate = 57600, receive_callback = None):
        # Attempt to find the serial port if not given
        if not port_name:
            port_list = serial.tools.list_ports.comports()
            for p in port_list:
                if "USB Serial Port" in p.description:
                    port_name = p.device
                elif "FT230X Basic UART"  in p.description:
                    port_name = p.device
        if port_name is None:
            print "USB serial port not found"
            raise Exception
        # open the serial port
        self.serial_port = serial.Serial(port_name, baud_rate, timeout=0.1)
        self.receive_callback = receive_callback
        if self.serial_port is None:
            return False
        # start the receive thread
        self.active = True
        self.thread = threading.Thread(target=self.receive_thread)
        self.thread.daemon = True
        self.thread.start()


    def close(self):
        self.active = False
        self.serial_port.close()
        self.thread.join(1.0)

    def write(self, data):
        self.serial_port.write(bytearray(data))

    def receive_thread(self):
        while self.active:
            data = self.serial_port.read(1)
            if data:
                data_list = [ord(x) for x in data]
                if self.receive_callback:
                    self.receive_callback(data_list)
                else:
                    print data_list



def main():
    port = "COM4"
    baud = "57600"
    args = sys.argv[1:]
    num_args = len(args)
    if num_args > 1:
        port = args[0]
    if num_args > 1:
        baud = args[1]
    serial_port = SerialPort()
    serial_port.open(port, baud)

    raw_input("Press Enter to continue...")

    serial_port.close()


if __name__ == "__main__":
    main()
