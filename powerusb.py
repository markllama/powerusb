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
import usb

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

class PowerUSBStrip():
    """
    A PowerUSB switched power strip
    """

    _vendor_id = 0x04d8
    _product_id = 0x003f

    def __init__(self, usb_device):
        self.usb_device = usb_device

    @staticmethod
    def strips():
        """
        Return the set of connected power strips
        """
        return [PowerUSBStrip(d) for b in usb.busses() for d in b.devices
                if d.idVendor == PowerUSBStrip._vendor_id 
                and d.idProduct == PowerUSBStrip._product_id]


###############################################################################
#
# PowerUSB Commands
#
###############################################################################

def strips():
    print PowerUSBStrip.strips()

###############################################################################
#
# MAIN
#
###############################################################################
if __name__ == "__main__":

    opts = parse_command_line()

    if opts.strips:
        strips()

    print opts
