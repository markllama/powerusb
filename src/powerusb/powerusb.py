#
# Library to control PowerUSB power strips
#
import sys, os, time


# manage inputs
from optparse import OptionParser

# work with XML DOM structures for configuration and automation
import lxml.etree as etree

import pyudev
import usb

class PowerUSBStrip:
    """
    Model a PowerUSB switchable power strip.
    """
    _vendor_id = 0x04d8
    _vendor_id_str = "04d8"
    _product_id = 0x003f
    _product_id_str = "003f"

    _buffer_len = 256
    _buffer_write = 65

    # strip commands
    _READ_FIRMWARE_VERSION = chr(0xa7)
    _READ_MODEL            = chr(0xaa)

    _READ_CURRENT          = chr(0xb1)
    _READ_CURRENT_CUM      = chr(0xb2)
    _RESET_CURRENT_COUNT   = chr(0xb3)
    _WRITE_OVERLOAD        = chr(0xb4)
    _READ_OVERLOAD         = chr(0xb5)
    _SET_CURRENT_RATIO     = chr(0xb6)
    _RESET_BOARD           = chr(0xc1)
    _SET_CURRENT_OFFSET    = chr(0xc2)

    _ALL_PORT_ON           = chr(0xa5)
    _ALL_PORT_OFF          = chr(0xa6)
    _SET_MODE              = chr(0xa8)
    _READ_MODE             = chr(0xa9)

    def __init__(self, device):
        """
        busnum: Integer - index of this bus
        devnum: Integer - index of this device on the bus
        """
        self._device = device
        self._file = None
        self._fd = None
        self._model = None

        self._outlets = [PowerUSBOutlet(self, 1),
                         PowerUSBOutlet(self, 2),
                         PowerUSBOutlet(self, 3)]

    def open(self):
        """Open the strip device file"""
        self._dh = self._device.open()
        self._dh.claimInterface(0)
        #self._fd = os.open(self._device.device_node, os.O_RDWR | os.O_APPEND | os.O_NONBLOCK)
        #self._file = open(self._device.device_node, 'r+')

    def close(self):
        """Close the strip device file"""
        #self._file.close()
        os.close(self._fd)

    def write(self, command):
        """Write a command to the power strip"""
        # the output buffer is 256 char, but the output is 65 bytes
        # the first byte is always a 0x00 and the trailing bytes are always
        # 0xff.
        # The remaining bytes in the middle are the message
        outbuf = chr(0x00) + command + (chr(0xff) * (64 - len(command)))
        #self._file.write(outbuf)
        #os.write(self._fd, outbuf)
        self._dh.bulkWrite(1, outbuf)

    def read(self):
        """Read from the power strip"""
        #return self._file.read(65)
        #return os.read(self._fd, self._buffer_write)
        return self._dh.bulkRead(1, 64)

    def model(self):
        """Retrieve the power strip model """
        if self._model == None:
            command = PowerUSBStrip._READ_MODEL
            self.write(command)
            outstring = self.read()
            self._model = int(outstring[0])
        return self._model

    @staticmethod
    def strip_devices_udev():
        """
        Search the udev list for power strip devices
        """
        context = pyudev.Context()
        devices = context.list_devices(subsystem="usb")
        strips = [d for d in devices 
                  if 'idVendor' in d.attributes.keys()
                  and d.attributes['idVendor'] == str(PowerUSBStrip._vendor_id_str)
                  and d.attributes['idProduct'] == PowerUSBStrip._product_id_str]
        
        return strips


    @staticmethod
    def strip_devices():
        return [d for d in usb.busses()[0].devices if d.idVendor == 0x04d8]

    @staticmethod
    def strips():
        """
        Return the set of strip objects
        """
        return [PowerUSBStrip(d) for d in PowerUSBStrip.strip_devices()]

    def outlets(self):
        return self._outlets

        

    def reset(self):
        """Reset the entire strip"""
        pass

    def firmware_verson(self):
        """Read the power strip firmware version"""
        pass

    def current(self):
        """Read the instantanious current from the whole strip"""
        pass

    def current_cumultive(self):
        """Read the cumulative current from the whole strip"""
        pass

    def reset_current_counter(self):
        """Reset the current counter"""
        pass

    def all_on(self):
        pass

    def all_off(self):
        pass

    def mode(self, value=None):
        """Set or get the 'mode'"""
        pass

    

class PowerUSBOutlet:
    """
    A single outlet on a PowerUSB strip
    """
    _ON_CODE      = ['A', 'C', 'E']
    _OFF_CODE     = ['B', 'D', 'P']
    _DEF_ON_CODE  = ['N', 'G', 'O']
    _DEF_OFF_CODE = ['F', 'Q', 'H']
    _READ         = [0xa1, 0xa2, 0xac]
    _READ_PWRUP   = [0xa3, 0xa4, 0xad]

    def __init__(self, strip, port):
        self._strip = strip
        self._port = port

    def on():
        """Turn the outlet on"""

    def off():
        """Turn the outlet off"""

    def default(state=None):
        """get or set the default state"""

    def state():
        """Retrive the power state of the outlet"""
        pass
    



if __name__ == "__main__":

    set_debug(HID_DEBUG_ALL)
    set_debug_stream(sys.stdout)
    
    #dev = usb.core.find(idVendor=vendor_id, idProduct=product_id, find_all=True)
    #print dev
    #strips = PowerUSBStrip.scanhid()
    #print strips
    interface = PowerUSBStrip.get_interface()
    interface.dump_tree(sys.stdout)
