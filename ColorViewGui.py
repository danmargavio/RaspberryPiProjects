from tkinter import *
import threading
from smbus2 import SMBus
import time

# Open i2c bus 1 and read one byte from address 80, offset 0
bus = SMBus(1)

DEVICE_ADDRESS = 0x52      #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MAIN_STATUS = 0x07  #main status register
DEVICE_REG_GREEN_0 = 0x0D  #Green measurement LSB
DEVICE_REG_RED_0   = 0X13
DEVICE_REG_BLUE_0  = 0x10

def convert_rgb_to_hex(r, g, b):
 return "#{:02x}{:02x}{:02x}".format(r, g, b)

def main():
	color_measurements = [0, 0, 0]
	# Init
	bus.write_byte_data(DEVICE_ADDRESS, 0x00, 0x07)
	#bus.write_byte_data(DEVICE_ADDRESS, 0x00, 0b0010)
	while True:
		color_measurements[0] = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_RED_0 + 0x01)
		color_measurements[1] = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_GREEN_0 + 0x01)
		color_measurements[2] = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_BLUE_0 + 0x01)

		print(color_measurements)

		print(hex(color_measurements[0]))

		root.configure(bg=convert_rgb_to_hex(color_measurements[0], color_measurements[1], color_measurements[2]))

		time.sleep(1)

root=Tk()

root.configure(bg='red')

upd_thread = threading.Thread(target=main, daemon=True)
upd_thread.start()

root.mainloop()
