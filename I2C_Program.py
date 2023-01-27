#!/usr/bin/env python3
#
# This is a NetworkTables client (eg, the DriverStation/coprocessor side).
# You need to tell it the IP address of the NetworkTables server (the
# robot or simulator).
#

import sys
import time
import numpy as np
import smbus2
from networktables import NetworkTables
from networktables.util import ntproperty

# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 2:
    print("Error: specify an IP to connect to!")
    exit(0)

ip = sys.argv[1]
NetworkTables.initialize(server=ip)

bus = smbus2.SMBus(1)
color_measurements = [0, 0, 0]
color_measurements_calibrated = [0, 0, 0]

DEVICE_ADDRESS = 0x52           #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MAIN_STATUS = 0x07   #main status register
DEVICE_REG_GREEN_0 = 0x0D       #Green measurement register LSB
DEVICE_REG_RED_0   = 0X13       #Red measurement register LSB
DEVICE_REG_BLUE_0  = 0x10       #Blue measurement register LSB

class SomeClient(object):
        red_raw = ntproperty("/SmartDashboard/colorSensorRed_raw", 0)
	green_raw = ntproperty("/SmartDashboard/colorSensorGreen_raw", 0)
	blue_raw = ntproperty("/SmartDashboard/colorSensorBlue_raw", 0)
	red_cal = ntproperty("/SmartDashboard/colorSensorRed_calibrated", 0)
	green_cal = ntproperty("/SmartDashboard/colorSensorGreen_calibrated", 0)
	blue_cal = ntproperty("/SmartDashboard/colorSensorBlue_calibrated", 0)

c = SomeClient()

def main():
	# Init
	bus.write_byte_data(DEVICE_ADDRESS, 0x00, 0x07)
	while True:
                # Read color data from the Rev Color Sensor V3. This matches the getColorRaw() method output from the ColorSensorV3 class
                color_measurements[0] = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_RED_0) + 256 * bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_RED_0 + 0x01) + 65536 * bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_RED_0 + 0x02)
                color_measurements[1] = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_GREEN_0) + 256 * bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_GREEN_0 + 0x01) + 65536 * bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_GREEN_0 + 0x02)
                color_measurements[2] = bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_BLUE_0) + 256 * bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_BLUE_0 + 0x01) + 65536 * bus.read_byte_data(DEVICE_ADDRESS, DEVICE_REG_BLUE_0 + 0x02)

		# calculate sum of all 3 channels to be used for calibration
                total_output = np.sum(color_measurements)

		# First normalize the color measurements according to the total measured output. This matches the getColor() method output from the ColorSensorV3 class
                color_measurements_calibrated[0] = color_measurements[0]/total_output
                color_measurements_calibrated[1] = color_measurements[1]/total_output
                color_measurements_calibrated[2] = color_measurements[2]/total_output

                print(color_measurements)
                print(color_measurements_calibrated)

                c.red_raw, c.green_raw, c.blue_raw = color_measurements
                c.red_cal, c.green_cal, c.blue_cal = color_measurements_calibrated

                time.sleep(1)
		
if __name__ == "__main__":
	try:
		main()
	finally:
		bus.close()
