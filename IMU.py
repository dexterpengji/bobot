import time
from SerialDevice import SerialDevice

imu = SerialDevice("COM3", 19200, buffer_read_len=10, buffer_write_len=10, debug=True)
imu.start()
time.sleep(1)
imu.pause()
time.sleep(1)
imu.resume()
time.sleep(1)
imu.pause()
time.sleep(1)
imu.stop()