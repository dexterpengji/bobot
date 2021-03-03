# reference-threading: https://www.cnblogs.com/scolia/p/6132950.html
import serial
import serial.tools.list_ports
import time
import threading

class SerialDevice(threading.Thread):
    def __init__(self, 
                port, 
                bode,  
                buffer_read_len, 
                buffer_write_len,
                debug=True):
        super(SerialDevice, self).__init__()
        self.__flag = threading.Event() # flag to pause
        self.__flag.set() # set to be true
        self.__running = threading.Event() # flag to stop
        self.__running.set() # set to be true
        self.debug = debug
        # find all serial ports
        if self.debug: 
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
            if self.debug: print("Failed to start Serial Port, will try again in 1 second.")
            time.sleep(1)
            self.ser.open()
        if self.debug: print("Serial Port started")
        # init buffers
        self.buffer_read = [] # element is self.data
        self.buffer_read_len = buffer_read_len
        self.buffer_write = [] # to be writen to serial port
        self.buffer_write_len = buffer_write_len
        # data structure
        self.data = [] # timestamp_system, timestamp_hardware, x_a, y_a, z_a, x_g, y_g, z_g, x_m, y_m, z_m

    
    def parse(self, data):
        output = data[:-2].decode('utf-8').split(',')
        output.insert(0, time.time())
        return output


    def write(self, data):
        # keep buffer_read size = expected_buffer_size - 1
        # add data to the tail of the writing buffer
        # return dumped data
        if len(self.buffer_write) > self.buffer_write_len:
            data_dumped = self.buffer_write[:-self.buffer_write_len + 1]
            self.buffer_write = self.buffer_write[-self.buffer_write_len + 1:]
        self.buffer_write.append(data)
        return data_dumped


    def get(self):
        if self.buffer_read:
            bufferred_data = self.buffer_read.copy()
            self.buffer_read = []
            return bufferred_data
        else:
            return None


    def run(self):
        while self.__running.isSet():
            self.__flag.wait()
            # keep buffer_read size = expected_buffer_size - 1
            if len(self.buffer_read) >= self.buffer_read_len:
                self.buffer_read = self.buffer_read[-self.buffer_read_len + 1:]
            # read data to buffer
            data_raw = self.ser.readline()
            data_parsed = self.parse(data_raw)
            self.buffer_read.append(data_parsed)
            # check if need to write data to serial
            if self.buffer_write:
                data_to_write = self.buffer_write.pop(0)
                self.ser.write(str.encode(str(data_to_write)))
            if self.debug:
                system_time_sub_hardware_time = data_parsed[0] - float(data_parsed[1])/1000 # to estimate time drift
                print(data_raw, data_parsed, len(self.buffer_read), self.buffer_write, len(self.buffer_write), system_time_sub_hardware_time)
    
    def pause(self):
        self.__flag.clear() # clear __flag to block the thread

    def resume(self):
        self.__flag.set() # set __flag to stop blocking the thread
        
    def stop(self):
        self.__flag.set() # step 1: resume, if it's been paused
        self.__running.clear() # step 2: set __running as False, exit    
