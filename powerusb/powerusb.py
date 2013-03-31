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
import hidapi

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
    
    _sleep_duration = 0.020 # seconds

    def __init__(self, hid_device=None):
        self.hid_device = hid_device
        self.socket = [None]
        for socket_num in range(1,4):
            self.socket.append(PowerUSBSocket(self, socket_num))

    @property
    def device(self):
        return self.hid_device

    @property
    def busnum(self):
        return self.hid_device.busnum

    @property
    def devnum(self):
        return self.hid_device.devnum

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
        time.sleep(PowerUSBStrip._sleep_duration)
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
        return self.hid_device['manufacturer']
    
    @property
    def product(self):
        return self.hid_device['product']

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
        hid_devices = hidapi.hid_enumerate(
            PowerUSBStrip._vendor_id,
            PowerUSBStrip._product_id
            )
        return [PowerUSBStrip(d) for d in hid_devices]
        
    def __str__(self):
        return "%d:%d, %-9s, FWVer: %3s, Curr(mA) %5.1f, Power(KWh): %4.2f, %3s, %3s, %3s" % (
            self.busnum,
            self.devnum,
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
        strip.set("busnum", str(self.busnum))
        strip.set("devnum", str(self.devnum))

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

    _on_cmd = ['A', 'C', 'E']
    _off_cmd = ['B', 'D', 'P']
    
    _defon_cmd = ['N', 'G', 'O']
    _defoff_cmd = ['F', 'Q', "H"]
    
    _state_cmd = [chr(0xa1), chr(0xa2), chr(0xac)]
    _defstate_cmd = [chr(0xa3), chr(0xa4), chr(0xad)]

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
        print "%d device(s) connected" % len(strips)
        for i in range(0, len(strips)):
            strip = strips[i]
            strip.open()
            print "%d) %s" % (i, strip)
            strip.close()

    elif format == "xml":
        
        stripxml = etree.Element("powerstrips")
        for i in range(0, len(strips)):
            strip = strips[i]
            strip.open()
            stripxml.append(strip.xml())
            strip.close()

        etree.dump(stripxml, pretty_print=True)
        print ""
        

