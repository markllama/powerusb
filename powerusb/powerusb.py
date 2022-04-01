#!/usr/bin/env python
from __future__ import print_function
#
# Manage PowerUSB power strips.
#  http://pwrusb.com
#
# Adapted from PowerUSB Linux source code
#
# Author: Mark Lamourine <markllama@gmail.com>
# 
# Copyright 2013
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

###############################################################################
#
# PowerUSB Objects
#
###############################################################################
import time
import lxml.etree as etree
import json
#import powerusb.hidapi as hidapi
import hid

class PowerUSBStrip(object):

    _vendor_id = 0x04d8
    _product_id = 0x003f

    _model = [None, "Basic", "Digital IO", "Computer Watchdog", "Smart Pro"]

    _power_state = ["off", "on"]

    _READ_FIRMWARE_VER	 = b'\xa7'
    _READ_MODEL		 = b'\xaa'

    _READ_CURRENT	 = b'\xb1'
    _READ_CURRENT_CUM	 = b'\xb2'
    _RESET_CURRENT_COUNT = b'\xb3'
    _WRITE_OVERLOAD      = b'\xb4'
    _READ_OVERLOAD	 = b'\xb5'
    _SET_CURRENT_RATIO	 = b'\xb6'
    _RESET_BOARD	 = b'\xc1'
    _SET_CURRENT_OFFSET	 = b'\xc2'

    _ALL_PORT_ON	 = b'\xa5'
    _ALL_PORT_OFF	 = b'\xa6'
    _SET_MODE		 = b'\xa8'
    _READ_MODE           = b'\xa9'

    # Digital IO
    _SET_IO_DIRECTION	 = b'\xd1'
    _SET_IO_OUTPUT	 = b'\xd3'
    _GET_IO_INPUT	 = b'\xd4'
    _SET_IO_CLOCK        = b'\xd5'
    _GET_IO_OUTPUT	 = b'\xd6'
    _SET_IO_TRIGGER	 = b'\xd7'
    _SET_IO_SETPLC	 = b'\xd8'
    _SET_IO_GETPLC	 = b'\xd9'
    _SET_IO_CLRPLC	 = b'\xda'

    # Watchdog
    _START_WDT		 = b'\x90'
    _STOP_WDT		 = b'\x91'
    _POWER_CYCLE	 = b'\x92'
    _READ_WDT 		 = b'\x93'	# retrun the all status.
    _HEART_BEAT		 = b'\x94'
    _SHUTDOWN_OFFON	 = b'\x95'

    # SMART
    _SET_ONOFF		 = b'\x81'
    _GET_ONOFF		 = b'\x82'
    _SET_FREQ		 = b'\x83'
    _SET_ONOFFMODE	 = b'\x84'
    _SET_MODE_SMART	 = b'\x85'
    _SET_TVLIMIT	 = b'\x86'
    _SET_DATETIME	 = b'\x87'
    _DISP_TEXT		 = b'\x88'
    _SET_PASS		 = b'\x89'
    
    _sleep_duration = 0.020 # seconds
    _read_timeout = 100 # milliseconds

    _instance_variables = [
        'path', 'vendor_id', 'product_id', 'serial_number', 'release_number',
        'manfuracturer_string', 'product_string', 'usage_page', 'usage', 'interface_number'
        ]
    
    def __init__(self, **kwargs):
        # Parse kwargs into instance variables
        #
        # ['
        for ivname in PowerUSBStrip._instance_variables:
            self.__dict__['_' + ivname] = kwargs[ivname] if ivname in kwargs else None
        self._device = hid.device(self._path)
        self.socket = [None]
        for socket_num in range(1,4):
            self.socket.append(PowerUSBSocket(self, socket_num))

    @property
    def device(self):
        return self._device

    @property
    def path(self):
        return self._path.decode('UTF-8')

    def open(self):
        self._device.open_path(self._path)

    def close(self):
        self._device.close()

    def read(self):
        instr = self._device.read(64, PowerUSBStrip._read_timeout)
        return instr

    def write(self, outstr):
        self._device.write(outstr + (b'\xff' * 63))

    @property
    def model(self):
        self.write(PowerUSBStrip._READ_MODEL)
#        time.sleep(PowerUSBStrip._sleep_duration)
        inbuffer = self.read()
        return PowerUSBStrip._model[inbuffer[0]]

    @property
    def firmware_version(self):
        self.write(PowerUSBStrip._READ_FIRMWARE_VER)
        time.sleep(PowerUSBStrip._sleep_duration)
        inbuffer = self.read()
        return "%d.%d" % (inbuffer[0], inbuffer[1])

    @property
    def current(self):
        """Instantanious Current (mA)"""
        self.write(PowerUSBStrip._READ_CURRENT)
        time.sleep(PowerUSBStrip._sleep_duration)
        inbuffer = self.read()
        if len(inbuffer) > 0:
            I = inbuffer[0] << 8 | inbuffer[1]
        else:
            I = 0
        return I

    @property
    def power(self):

        self.write(PowerUSBStrip._READ_CURRENT_CUM)
        time.sleep(PowerUSBStrip._sleep_duration)
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

    def reset_power(self):
        """Clear the accumulate power measurement"""
        self.write(PowerUSBStrip._READ_CURRENT_CUM)
        time.sleep(PowerUSBStrip._sleep_duration)

    @property
    def manufacturer(self):
        return self._device.get_manufacturer_string()
    
    @property
    def product(self):
        return self._device.get_product_string()

    def all_on(self):
        self.write(PowerUSBStrip._ALL_PORT_ON)
        time.sleep(PowerUSBStrip._sleep_duration)

    def all_off(self):
        self.write(PowerUSBStrip._ALL_PORT_OFF)
        time.sleep(PowerUSBStri._sleep_duration)

    def reset(self):
        self.write(PowerUSBStrip._RESET_BOARD)
        time.sleep(PowerUSBStrip._sleep_duration)

    @property
    def overload(self):
        self.write(PowerUSBStrip._READ_OVERLOAD)
        time.sleep(PowerUSBStrip._sleep_duration)
        inbuffer = self.read()
        return int(inbuffer[0])
        
    @overload.setter
    def overload(self, ol):
        self.write(int(ol))
        time.sleep(PowerUSBStri._sleep_duration)



    @staticmethod
    def strips():
        """
        Return the set of connected power strips
        """
        hid_devices = hid.enumerate(
            PowerUSBStrip._vendor_id,
            PowerUSBStrip._product_id
            )
        return [PowerUSBStrip(**d) for d in hid_devices]
        
    def __str__(self):
        return "%s %-9s, FWVer: %3s, Curr(mA) %5.1f, Power(KWh): %4.2f, %3s, %3s, %3s" % (
            self.path,
            self.model, 
            self.firmware_version,
            self.current,
            self.power,
            self.socket[1].power,
            self.socket[2].power,
            self.socket[3].power
            )

    def xml(self):

        strip = etree.Element("powerstrip")
        strip.set("model", str(self.model))
        strip.set("fw_version", str(self.firmware_version))
        strip.set("path", self.path)

        current = etree.Element("current")
        current.text = str(self.current)
        strip.append(current)
        
        power = etree.Element("power")
        power.text = str(self.power)
        strip.append(power)

        sockets = etree.Element("sockets")
        for socket_number in range(1,4):
            sockets.append(self.socket[socket_number].xml())
        strip.append(sockets)

        return strip

class PowerUSBSocket(object):

    _on_cmd = [b'A', b'C', b'E']
    _off_cmd = [b'B', b'D', b'P']
    
    _defon_cmd = [b'N', b'G', b'O']
    _defoff_cmd = [b'F', b'Q', b'H']
    
    _state_cmd = [b'\xa1', b'\xa2', b'\xac']
    _defstate_cmd = [b'\xa3', b'\xa4', b'\xad']

    _state_str = ['off', 'on']

    def __init__(self, strip, socket_num):
        self._strip = strip
        self._socket_num = socket_num

    @property
    def strip(self):
        return self._strip

    @property
    def socket_num(self):
        return self.socket_num

    @property
    def power(self):
        """Retrieve and return the power state of the socket"""
        self._strip.write(PowerUSBSocket._state_cmd[self._socket_num - 1])
        time.sleep(PowerUSBStrip._sleep_duration)
        reply = self._strip.read()
        return PowerUSBSocket._state_str[reply[0]]

    @power.setter
    def power(self, on=None):
        """Set the power state on a socket"""
        if on == True or on == "on":
            self._strip.write(PowerUSBSocket._on_cmd[self._socket_num - 1])
        elif on == False or on == "off":
            self._strip.write(PowerUSBSocket._off_cmd[self._socket_num - 1])

    @property
    def default(self):
        """Retrieve and return the default power state of the socket"""
        self._strip.write(PowerUSBSocket._defstate_cmd[self._socket_num - 1])
        time.sleep(PowerUSBStrip._sleep_duration)
        reply = self._strip.read()
        return PowerUSBSocket._state_str[reply[0]]

    @default.setter
    def default(self, on=None):
        if on == "on":
            self._strip.write(PowerUSBSocket._defon_cmd[self._socket_num - 1])
        elif on == "off":
            self._strip.write(PowerUSBSocket._defoff_cmd[self._socket_num - 1])

    def xml(self):
        socket = etree.Element("socket")
        socket.set("number", str(self._socket_num))

        power = etree.Element("power")
        power.text = self.power
        socket.append(power)

        default = etree.Element("default")
        default.text = self.default
        socket.append(default)

        return socket

###############################################################################
#
# PowerUSB Commands
#
###############################################################################

def strip_status(format):
    strips = PowerUSBStrip.strips()
    
    if format == "text":
        print("%d device(s) connected" % len(strips))
        for i in range(0, len(strips)):
            strip = strips[i]
            strip.open()
            print("%d) %s" % (i, strip))
            strip.close()

    elif format == "xml":
        
        stripxml = etree.Element("powerstrips")
        for i in range(0, len(strips)):
            strip = strips[i]
            strip.open()
            stripxml.append(strip.xml())
            strip.close()

        etree.dump(stripxml, pretty_print=True)
        print()
        

