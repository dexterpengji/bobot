import serial
import serial.tools.list_ports
import numpy
import time

class IMU:
    def __init__(self, port, bode, debug=True):
        # find all serial ports
        if debug: 
            ports = serial.tools.list_ports.comports()
            for p in ports:
                print(p.device)
            print(len(ports), 'ports found')
        # start serial port
        self.port = port
        self.bode = bode
        self.ser = serial.Serial(self.port, 
                                self.bode, 
                                timeout=1,
                                parity=serial.PARITY_EVEN,
                                rtscts=1
                                )
        while not self.ser.is_open:
            if debug: print("Failed to start Serial Port, will try again in 1 second.")
            time.sleep(1)
            self.ser.open()
        if debug: print("Serial Port started")
        self.status = 1 # 0: stopped, 1: reading, 2: writing
        self.data_raw = {"data":None, "time_stamp":None} # raw data from serial port - IMU
        self.data_parsed = [] # x_a, y_a, z_a, x_g, y_g, z_g, x_m, y_m, z_m, temperature, timestamp


    def read(self):
        self.data = self.ser.readline() # end with '\n'
        return self.data


    def parse(self, _in):
        return _in

    
    def write(self, _in):
        self.ser.write(bytes(_in, 'utf-8'))


    def spin(self):
        while True:
            if self.status == 0: # stopped
                break
            elif self.status == 1: # reading
                self.data_raw = self.ser.readline()
                print(self.data_raw)
                self.data_parsed = self.parse(self.data_raw)
            elif self.status == 2: # writing
                self.write()
                

if __name__ == "__main__":
    imu = IMU("COM3", 19200)

