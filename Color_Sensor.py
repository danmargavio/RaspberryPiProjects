"""
REV Color V3 to NetTables w/ GUI
By: Kevin Ahr
"""

import threading
import time
import tkinter as tk
import argparse
import logging

from networktables import NetworkTables
from networktables.util import ntproperty

__version__ = "1.0"
__author__ = "Kevin Ahr"

# device properties
DEVICE_ADDRESS = 0x52  # 7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MAIN_STATUS = 0x07  # main status register
MAIN_CTRL = 0x00  # operation mode control
LS_DATA_GREEN_0 = 0x0D  # First Green Register
LS_DATA_RED_0 = 0x13  # First Red Register
LS_DATA_BLUE_0 = 0x10  # First Blue Register
LS_DATA_IR_0 = 0x0A
LS_DATA_GREEN_1 = 0x0E  # Second Green Register
LS_DATA_RED_1 = 0x14  # Second Red Register
LS_DATA_BLUE_1 = 0x11  # Second Blue Register
PS_DATA_0 = 0x08
PS_DATA_1 = 0x09

global root, ir, data_label, prox_label

# parse command line args
parser = argparse.ArgumentParser()
parser.add_argument("ip", help="ip address to connect to")
parser.add_argument("-ir", "--ir", action="store_true", help="enable ir")
parser.add_argument("-p", "--proximity", action="store_true", help="enable prox. sensor")
parser.add_argument("-g", "--gui", action="store_true", help="show color viewer gui")
parser.add_argument("-wp", "--window-properties", default="", type=str,
                    help="CSV formatted window properties")
parser.add_argument("-irp", "--ir-window-properties", default="", type=str,
                    help="CSV formatted ir window properties")
parser.add_argument("-vi", "--virtual", action="store_true", help="use rng instead of sensor")
parser.add_argument("-v", "--verbose", action="store_true", help="use verbose logging")
parser.add_argument("-r", "--rate", default=1, type=float, help="sensor polling rate")
parser.add_argument("-rw", "--red-weight", default=1, type=float, help="weight of red channel")
parser.add_argument("-gw", "--green-weight", default=1, type=float, help="weight of green channel")
parser.add_argument("-bw", "--blue-weight", default=1, type=float, help="weight of blue channel")
parser.add_argument("-iw", "--ir-weight", default=1, type=float, help="weight of IR channel")
args = parser.parse_args()


# NT Client
class Client(object):
    """Demonstrates an object with magic networktables properties"""
    red = ntproperty("/SmartDashboard/colorSensorRed", 0)
    green = ntproperty("/SmartDashboard/colorSensorGreen", 0)
    blue = ntproperty("/SmartDashboard/colorSensorBlue", 0)
    if args.ir:
        ir = ntproperty("/SmartDashboard/colorSensorIr", 0)

    if args.proximity:
        prox = ntproperty("/SmartDashboard/colorSensorProx", 0)


def rgb_to_hex(r, g, b):
    """Convert RGB Value to Hex Color Codes"""
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def get_rgb():
    colors = [0, 0, 0, 0]
    colors[0] = bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_RED_0) + 256 * bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_RED_0 + 0x01) + 65536 * bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_RED_0 + 0x02)
    colors[1] = bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_GREEN_0) + 256 * bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_GREEN_0 + 0x01) + 65536 * bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_GREEN_0 + 0x02)
    colors[2] = bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_BLUE_0) + 256 * bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_BLUE_0 + 0x01) + 65536 * bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_BLUE_0 + 0x02)
    colors[3] = bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_IR_0) + 256 * bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_IR_0 + 0x01) + 65536 * bus.read_byte_data(DEVICE_ADDRESS, LS_DATA_IR_0 + 0x02)
    return colors

def get_prox():
    data = bus.read_byte_data(DEVICE_ADDRESS, PS_DATA_0) + 256 * bus.read_byte_data(DEVICE_ADDRESS, PS_DATA_1)
    return data


def clamp(n, minn, maxn):
    """Clamp Input to Min/Max"""
    return max(min(maxn, n), minn)


def update_vals():
    color_measurements = {"r": 0, "g": 0, "b": 0}

    if args.ir:
        color_measurements["ir"] = 0

    # Init
    if not args.virtual:
        bus.write_byte_data(DEVICE_ADDRESS, MAIN_CTRL, 0x07)
        bus.write_byte_data(DEVICE_ADDRESS, 0x05, 0b00000100) # set gain to 18
    while True:
        if not args.virtual:
            colors = get_rgb()
            color_measurements["r"] = round(clamp(colors[0] / 2048 * args.red_weight,0, 255))
            color_measurements["g"] = round(clamp(colors[1] / 2048 * args.green_weight, 0, 255))
            color_measurements["b"] = round(clamp(colors[2] / 2048 * args.blue_weight, 0, 255))
            if args.ir:
                color_measurements["ir"] = round(clamp(colors[3] / 2048 * args.ir_weight, 0, 255))
        else:
            color_measurements["r"] = round(clamp(random.randint(0, 255) * args.red_weight, 0, 255))
            color_measurements["g"] = round(clamp(random.randint(0, 255) * args.green_weight, 0, 255))
            color_measurements["b"] = round(clamp(random.randint(0, 255) * args.blue_weight, 0, 255))
            if args.ir:
                color_measurements["ir"] = round(clamp(random.randint(0, 255) * args.ir_weight, 0, 255))

        if args.proximity:
            prox = get_prox()
            c.prox = prox

        c.red, c.green, c.blue, c.ir = color_measurements['r'], color_measurements['g'], color_measurements['b'], color_measurements['ir']

        # log data
        logging.log(logging.DEBUG, f"Data: {color_measurements}")
        if args.proximity:
            logging.log(logging.DEBUG, f"Prox: {prox}")

        if args.gui:
            root.configure(bg=rgb_to_hex(color_measurements["r"], color_measurements["g"], color_measurements["b"]))
            data_label.configure(text=color_measurements)

            if args.ir:
                ir.configure(bg=rgb_to_hex(color_measurements["ir"], color_measurements["ir"], color_measurements["ir"]))

            if args.proximity:
                prox_label.configure(text=f"prox: {prox}")

        time.sleep(args.rate)


def main():
    global root, ir, data_label, prox_label

    if args.gui:
        root = tk.Tk()
        root.title("ColorView")
        root.geometry("240x240")

        info_frame = tk.Frame(root)
        info_frame.configure(relief=tk.SUNKEN, borderwidth=3)
        info_frame.pack()

        data_label = tk.Label(master=info_frame, text="DATA")
        data_label.pack()

        if args.proximity:
            prox_frame = tk.Frame(root)
            prox_frame.configure(relief=tk.SUNKEN, borderwidth=3)
            prox_frame.pack()

            prox_label = tk.Label(master=prox_frame, text="PROX")
            prox_label.pack()

        for prop in args.window_properties.split(','):
            prop = prop.split(":")
            if prop[0] == "size":
                root.geometry(prop[1])
            elif prop[0] == "title":
                root.title(prop[1])

        if args.ir:
            ir = tk.Toplevel()
            ir.title("IrView")
            ir.geometry("240x100")

            for prop in args.ir_window_properties.split(','):
                prop = prop.split(":")
                if prop[0] == "size":
                    ir.geometry(prop[1])
                elif prop[0] == "title":
                    ir.title(prop[1])

        # start thread
        thread = threading.Thread(target=update_vals, daemon=True)
        thread.start()

        root.mainloop()
    else:
        update_vals()


if __name__ == "__main__":
    # set up logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        from smbus2 import SMBus
    except ImportError as err:
        logging.warning(f"Could not import SMBus2: {err}")

    # open i2c bus
    if not args.virtual:
        try:
            bus = SMBus(1)
        except Exception as err:
            logging.critical(f"Could not initialize SMBus: {err}")
    else:
        import random

    # set up network tables
    NetworkTables.initialize(server=args.ip)
    c = Client()

    main()
