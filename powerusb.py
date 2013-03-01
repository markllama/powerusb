#!/usr/bin/python
"""
Control one or more PowerUSB power strips

* display the set of connected strips

* Turn a socket on or off
* Read the power state of a socket
* Set the default for a socket
* Turn an entire strip on or off
* read the cumulative power from a strip

* Assign a label to a strip

powerusb --strips

powerusb --status <strip>[:<socket>]

powerusb --socket <strip>:<socket> (-on|-off) [--default]

powerusb --meter <strip> [--cumulative|--reset]]

"""

import argparse
import re
import time
import hidapi

##############################################################################
#
# Argument Parsing
#
##############################################################################

class CommandAction(argparse.Action):
    """
    Parse one of the 5 command actions
    """
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.command = re.sub("^--", "", option_string)
        namespace.socket = values

def parse_command_line():
    """Parse the command line arguments"""

    parser = argparse.ArgumentParser(description="Manage power strips")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--xml", "-x", action="store_true")
    parser.add_argument("--json", "-j", action="store_true")
    cmd_group = parser.add_mutually_exclusive_group()
    cmd_group.add_argument("--strips", "-l", action="store_true")
    cmd_group.add_argument("--status", '-s', metavar="SOCKETSPEC", 
                           action=CommandAction, dest="command", nargs="+")
    cmd_group.add_argument("--socket", "-p", metavar="SOCKETSPEC",
                           action=CommandAction, dest="command", nargs="+")
    cmd_group.add_argument("--meter", "-m", metavar="SOCKETSPEC",
                           action=CommandAction, dest="command", nargs="+")
    on_off = parser.add_mutually_exclusive_group()
    on_off.add_argument("--on", dest="on", action="store_true", default=None) 
    on_off.add_argument("--off", dest="on", action="store_false")
    parser.add_argument("--default", action="store_true")
    parser.add_argument("--cumulative", action="store_true")
    parser.add_argument("--reset", action="store_true")
    return parser.parse_args()

###############################################################################
#
# HID Device Library
#
###############################################################################


###############################################################################
#
# PowerUSB Objects
#
###############################################################################

class PowerUSBStrip(object):

    _vendor_id = 0x04d8
    _product_id = 0x003f

    _model = [None, "Basic", "Digital IO", "Computer Watchdog", "Smart Pro"]

    _power_state = ["off", "on"]

    _READ_FIRMWARE_VER	 = chr(0xa7)
    _READ_MODEL		 = chr(0xaa)

    _READ_CURRENT	 = chr(0xb1)
    _READ_CURRENT_CUM	 = chr(0xb2)
    _RESET_CURRENT_COUNT = chr(0xb3)
    _WRITE_OVERLOAD      = chr(0xb4)
    _READ_OVERLOAD	 = chr(0xb5)
    _SET_CURRENT_RATIO	 = chr(0xb6)
    _RESET_BOARD	 = chr(0xc1)
    _SET_CURRENT_OFFSET	 = chr(0xc2)

    _ALL_PORT_ON	 = chr(0xa5)
    _ALL_PORT_OFF	 = chr(0xa6)
    _SET_MODE		 = chr(0xa8)
    _READ_MODE           = chr(0xa9)

    # Digital IO
    _SET_IO_DIRECTION	 = chr(0xd1)
    _SET_IO_OUTPUT	 = chr(0xd3)
    _GET_IO_INPUT	 = chr(0xd4)
    _SET_IO_CLOCK        = chr(0xd5)
    _GET_IO_OUTPUT	 = chr(0xd6)
    _SET_IO_TRIGGER	 = chr(0xd7)
    _SET_IO_SETPLC	 = chr(0xd8)
    _SET_IO_GETPLC	 = chr(0xd9)
    _SET_IO_CLRPLC	 = chr(0xda)

    # Watchdog
    _START_WDT		 = chr(0x90)
    _STOP_WDT		 = chr(0x91)
    _POWER_CYCLE	 = chr(0x92)
    _READ_WDT 		 = chr(0x93)	# retrun the all status.
    _HEART_BEAT		 = chr(0x94)
    _SHUTDOWN_OFFON	 = chr(0x95)

    # SMART
    _SET_ONOFF		 = chr(0x81)
    _GET_ONOFF		 = chr(0x82)
    _SET_FREQ		 = chr(0x83)
    _SET_ONOFFMODE	 = chr(0x84)
    _SET_MODE_SMART	 = chr(0x85)
    _SET_TVLIMIT	 = chr(0x86)
    _SET_DATETIME	 = chr(0x87)
    _DISP_TEXT		 = chr(0x88)
    _SET_PASS		 = chr(0x89)
    
    def __init__(self, hid_device):
        self.hid_device = hid_device
        self.sockets = []
        for socket_num in range(1,4):
            self.sockets.append(PowerUSBSocket(self, socket_num))

    @property
    def device(self):
        return self.hid_device

    def open(self):
        self.hid_device.open()

    def close(self):
        self.hid_device.close()

    def read(self):
        instr = self.hid_device.read(64)
        return instr

    def write(self, outstr):
        self.hid_device.write(outstr + chr(0xff) * (64 - len(outstr)))

    @property
    def model(self):
        self.write(PowerUSBStrip._READ_MODEL)
        time.sleep(0.020)
        inbuffer = self.read()
        return PowerUSBStrip._model[inbuffer[0]]

    @property
    def firmware_version(self):
        self.write(PowerUSBStrip._READ_FIRMWARE_VER)
        time.sleep(0.020)
        inbuffer = self.read()
        return "%d.%d" % (inbuffer[0], inbuffer[1])

    @property
    def current(self):
        """Instantanious Current (mA)"""
        self.write(PowerUSBStrip._READ_CURRENT)
        time.sleep(0.020)
        inbuffer = self.read()
        if len(inbuffer) > 0:
            I = inbuffer[0] << 8 | inbuffer[1]
        else:
            I = 0
        return I

    @property
    def power(self):

        self.write(PowerUSBStrip._READ_CURRENT_CUM)
        time.sleep(0.020)
        inbuffer = self.read()
        if len(inbuffer) >=4:
            n = inbuffer[0]<<24 | inbuffer[1]<<16 | inbuffer[2]<<8 | inbuffer[3]
        else:
            n = 0

        # convert mA*minute to kWh (at 120V)
        # (mAmin) / 1000 -> Amin
        # (Amin) / 60 = A*h
        # (Ah) * 120V = wh
        # (wh) / 1000 = kwh
        #  (n / 60) * 120 / 1000 / 1000
        #  (n * 2) / 1000 / 1000
        return float(n) / 500000.0

    @property
    def manufacturer(self):
        return self.hid_device['manufacturer']
    
    @property
    def product(self):
        return self.hid_device['product']

    @staticmethod
    def strips():
        """
        Return the set of connected power strips
        """
        hid_devices = hidapi.hid_enumerate(
            PowerUSBStrip._vendor_id,
            PowerUSBStrip._product_id
            )
        return [PowerUSBStrip(d) for d in hid_devices]
        
    @property
    def status(self):
        return "Model: %10s, FW Version: %3s, Curr.(mA) %6.1f, Power (KWh): %5.2f" % (
            self.model, 
            self.firmware_version,
            self.current,
            self.power
            )

class PowerUSBSocket(object):

    _on_cmd = ['A', 'C', 'E']
    _off_cmd = ['B', 'D', 'P']
    
    _defon_cmd = ['N', 'G', 'O']
    _defoff_cmd = ['F', 'Q', "H"]
    
    _state_cmd = [chr(0xa1), chr(0xa2), chr(0xac)]
    _defstate_cmd = [chr(0xa3), chr(0xa4), chr(0xad)]

    def __init__(self, strip, socket_num):
        self._strip = strip
        self._socket_num = socket_num

    @property
    def power(self):
        """Retrieve and return the power state of the socket"""
        self.strip.write(PowerUSBSocket._state_cmd[self._socket_num - 1])
        time.sleep(0.020)
        reply = self.strip.read(64)
        return int(reply[0])

    @power.setter
    def power(self, on=None):
        """Set the power state on a socket"""
        if on == True:
            self._strip.write(PowerUSBSocket._on_cmd[self._socket_num - 1])
        elif on == False:
            self._strip.write(PowerUSBSocket._off_cmd[self._socket_num - 1])


###############################################################################
#
# PowerUSB Commands
#
###############################################################################

def strips():
    strips = PowerUSBStrip.strips()
    
    print "%d device(s) connected" % len(strips)
    for i in range(0, len(strips)):
        strip = strips[i]
        strip.open()
        print "%d) %s" % (i, strip.status)
        strip.close()

###############################################################################
#
# MAIN
#
###############################################################################
if __name__ == "__main__":

    opts = parse_command_line()

    print opts

    if opts.strips == True:
        strips()
    elif opts.command == 'status':
        # validate the socket spec
        print opts.command + ": " + opts.socket[0]
    elif opts.command == 'socket':
        print opts.command + ": " + opts.socket[0]
